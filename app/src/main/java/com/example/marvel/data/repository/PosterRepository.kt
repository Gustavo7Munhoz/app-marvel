package com.example.marvel.data.repository

import android.content.Context
import android.content.SharedPreferences
import com.example.marvel.BuildConfig
import com.example.marvel.model.FilmeModel
import com.google.gson.JsonObject
import com.google.gson.JsonParser
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import javax.inject.Inject
import javax.inject.Singleton

sealed class PosterResult(val url: String?, val fonte: String) {
    class ItemUrl(url: String) : PosterResult(url, "ITEM_PRECONFIGURADO")
    class Tmdb(url: String) : PosterResult(url, "TMDB_API")
    class Wikipedia(url: String) : PosterResult(url, "WIKIPEDIA_REST_API")
    class Cache(url: String, fonteOriginal: String) : PosterResult(url, "CACHE_LOCAL ($fonteOriginal)")
    object Placeholder : PosterResult(null, "PLACEHOLDER_LOCAL")
}

@Singleton
class PosterRepository @Inject constructor(
    @ApplicationContext private val context: Context,
    private val okHttpClient: OkHttpClient
) {
    private val prefs: SharedPreferences? by lazy {
        try {
            context.getSharedPreferences("poster_cache_prefs", Context.MODE_PRIVATE)
        } catch (_: Exception) {
            null
        }
    }

    /**
     * Resolve a URL do pôster para o filme/série fornecido, obedecendo a ordem de fallback:
     * 1. URL pré-definida no item (se válida e não vazia).
     * 2. Cache local (SharedPreferences).
     * 3. TMDB API (se chave disponível).
     * 4. Wikipedia REST API pública com User-Agent.
     * 5. Retorna null (para acionar o placeholder local #2A2A2A com claquete).
     */
    suspend fun obterPoster(
        filme: FilmeModel,
        forceRefresh: Boolean = false
    ): PosterResult = withContext(Dispatchers.IO) {
        // 1. Se o item já tiver uma URL de pôster válida
        val itemUrl = filme.posterUrl
        if (!itemUrl.isNullOrBlank() && itemUrl.startsWith("http", ignoreCase = true)) {
            return@withContext PosterResult.ItemUrl(itemUrl)
        }

        val tituloBusca = filme.tituloOriginal ?: filme.titulo ?: ""
        if (tituloBusca.isBlank()) {
            return@withContext PosterResult.Placeholder
        }

        val cacheKey = "poster_" + tituloBusca.lowercase().replace(Regex("[^a-z0-9]"), "_")

        // 2. Consulta Cache Local
        if (!forceRefresh) {
            val cachedUrl = prefs?.getString(cacheKey, null)
            val cachedFonte = prefs?.getString("${cacheKey}_fonte", "CACHE")
            if (!cachedUrl.isNullOrBlank() && cachedUrl != "PLACEHOLDER") {
                return@withContext PosterResult.Cache(cachedUrl, cachedFonte ?: "CACHE")
            }
        }

        val isSerie = filme.categoria?.contains("DISNEY", ignoreCase = true) == true ||
                filme.faseStatus?.contains("SÉRIE", ignoreCase = true) == true ||
                filme.faseStatus?.contains("SERIE", ignoreCase = true) == true

        // 3. Tenta TMDB API se houver chave configurada
        val tmdbKey = obterTmdbApiKey()
        if (!tmdbKey.isNullOrBlank()) {
            val tmdbUrl = buscarNoTmdb(tituloBusca, tmdbKey, isSerie)
            if (!tmdbUrl.isNullOrBlank()) {
                salvarEmCache(cacheKey, tmdbUrl, "TMDB_API")
                return@withContext PosterResult.Tmdb(tmdbUrl)
            }
        }

        // 4. Tenta Wikipedia REST API pública com User-Agent
        val wikiUrl = buscarNaWikipedia(tituloBusca, isSerie)
        if (!wikiUrl.isNullOrBlank()) {
            salvarEmCache(cacheKey, wikiUrl, "WIKIPEDIA_REST_API")
            return@withContext PosterResult.Wikipedia(wikiUrl)
        }

        // 5. Fallback para placeholder (não grava PLACEHOLDER em definitivo para permitir retentativas de rede)
        PosterResult.Placeholder
    }

    private fun salvarEmCache(key: String, url: String, fonte: String) {
        prefs?.edit()
            ?.putString(key, url)
            ?.putString("${key}_fonte", fonte)
            ?.apply()
    }

    private fun obterTmdbApiKey(): String? {
        return try {
            val field = BuildConfig::class.java.getField("TMDB_API_KEY")
            val key = field.get(null) as? String
            if (!key.isNullOrBlank()) key else null
        } catch (_: Exception) {
            null
        }
    }

    private fun buscarNoTmdb(titulo: String, apiKey: String, isSerie: Boolean): String? {
        return try {
            val tituloLimpo = limparTituloParaBusca(titulo)
            val encodedQuery = URLEncoder.encode(tituloLimpo, StandardCharsets.UTF_8.toString())
            val endpoint = if (isSerie) "tv" else "movie"
            val url = "https://api.themoviedb.org/3/search/$endpoint?api_key=$apiKey&query=$encodedQuery&language=pt-BR"

            val request = Request.Builder()
                .url(url)
                .get()
                .build()

            okHttpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return null
                val bodyStr = response.body?.string() ?: return null
                val json = JsonParser.parseString(bodyStr).asJsonObject
                val results = json.getAsJsonArray("results")
                if (results != null && results.size() > 0) {
                    val first = results[0].asJsonObject
                    val posterPath = first.get("poster_path")?.takeIf { !it.isJsonNull }?.asString
                    if (!posterPath.isNullOrBlank()) {
                        return "https://image.tmdb.org/t/p/w500$posterPath"
                    }
                }
            }
            null
        } catch (_: Exception) {
            null
        }
    }

    private fun buscarNaWikipedia(titulo: String, isSerie: Boolean): String? {
        val candidatos = gerarCandidatosWikipedia(titulo, isSerie)
        for (candidato in candidatos) {
            try {
                val encoded = URLEncoder.encode(candidato, StandardCharsets.UTF_8.toString())
                    .replace("+", "_")
                val url = "https://en.wikipedia.org/api/rest_v1/page/summary/$encoded"

                val request = Request.Builder()
                    .url(url)
                    .header("User-Agent", "MarvelApp/1.0 (android@shield-archive.marvel.internal)")
                    .get()
                    .build()

                okHttpClient.newCall(request).execute().use { response ->
                    if (response.isSuccessful) {
                        val bodyStr = response.body?.string() ?: return@use
                        val json = JsonParser.parseString(bodyStr).asJsonObject

                        // Tenta extrair thumbnail.source
                        val thumbObj = json.getAsJsonObject("thumbnail")
                        val thumbSource = thumbObj?.get("source")?.takeIf { !it.isJsonNull }?.asString
                        if (!thumbSource.isNullOrBlank()) {
                            return thumbSource
                        }

                        // Tenta extrair originalimage.source
                        val origObj = json.getAsJsonObject("originalimage")
                        val origSource = origObj?.get("source")?.takeIf { !it.isJsonNull }?.asString
                        if (!origSource.isNullOrBlank()) {
                            return origSource
                        }
                    }
                }
            } catch (_: Exception) {
                // Tenta próximo candidato
            }
        }
        return null
    }

    private fun gerarCandidatosWikipedia(tituloOriginal: String, isSerie: Boolean): List<String> {
        val candidatos = mutableListOf<String>()
        val tituloSemAsterisco = tituloOriginal.replace("*", "").trim()
        val baseUnder = tituloSemAsterisco.replace(" ", "_")
        val tituloSemDoisPontos = tituloSemAsterisco.replace(":", "")
        val baseSemDoisPontos = tituloSemDoisPontos.replace(" ", "_")

        val isPalavraUnica = !tituloOriginal.contains(" ") && !tituloOriginal.contains(":")

        // Para palavras únicas (ex: "Blade"), tenta qualificadores específicos antes do substantivo comum
        if (!isPalavraUnica) {
            if (tituloOriginal.contains("*")) {
                candidatos.add(tituloOriginal.replace(" ", "_"))
            }
            candidatos.add(baseUnder)
        }

        if (isSerie) {
            candidatos.add("${baseSemDoisPontos}_(miniseries)")
            candidatos.add("${baseSemDoisPontos}_(TV_series)")
            candidatos.add("${baseUnder}_(miniseries)")
        } else {
            candidatos.add("${baseSemDoisPontos}_(film)")
            candidatos.add("${baseSemDoisPontos}_(upcoming_film)")
            candidatos.add("${baseSemDoisPontos}_(character)")
            candidatos.add("${baseUnder}_(film)")
            if (tituloOriginal.contains("Secret Wars", ignoreCase = true)) {
                candidatos.add("Secret_Wars")
            }
        }

        if (isPalavraUnica) {
            candidatos.add(baseUnder)
        }

        return candidatos.distinct()
    }

    private fun limparTituloParaBusca(titulo: String): String {
        return titulo
            .replace("*", "")
            .replace(":", "")
            .replace("(", "")
            .replace(")", "")
            .trim()
    }
}
