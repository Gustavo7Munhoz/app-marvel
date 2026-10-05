package com.example.marvel

import android.content.Context
import com.example.marvel.data.repository.PosterRepository
import com.example.marvel.data.repository.PosterResult
import com.example.marvel.model.FilmeModel
import kotlinx.coroutines.runBlocking
import okhttp3.OkHttpClient
import org.junit.Assert.assertNotNull
import org.junit.Test
import java.lang.reflect.Proxy
import java.util.concurrent.TimeUnit

import android.content.ContextWrapper
import android.content.SharedPreferences

class PosterRepositoryTest {

    private fun createDummyContext(): Context {
        return object : ContextWrapper(null) {
            override fun getSharedPreferences(name: String?, mode: Int): SharedPreferences? = null
        }
    }

    @Test
    fun testPosterResolutionForAllItems() = runBlocking {
        val okHttpClient = OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build()

        val repository = PosterRepository(createDummyContext(), okHttpClient)

        val filmes = listOf(
            FilmeModel.criarLancamento("2026-12-18", "VINGADORES: DOOMSDAY", "Avengers: Doomsday", "FASE 6", "Sinopse", "CINEMA", false, "[EM PRODUÇÃO]"),
            FilmeModel.criarLancamento("2027-12-17", "VINGADORES: GUERRAS SECRETAS", "Avengers: Secret Wars", "FASE 6", "Sinopse", "CINEMA", false, "[NÍVEL 8]"),
            FilmeModel.criarLancamento(null, "BLADE", "Blade", "FASE 6", "Sinopse", "CINEMA", false, "[EM DESENVOLVIMENTO]"),
            FilmeModel.criarLancamento(null, "ARMOR WARS", "Armor Wars", "FASE 6", "Sinopse", "CINEMA", false, "[EM DESENVOLVIMENTO]"),
            FilmeModel.criarLancamento(null, "CORAÇÃO DE FERRO (IRONHEART)", "Ironheart", "FASE 5", "Sinopse", "DISNEY+", false, "[EM DESENVOLVIMENTO]")
        )

        println("=== TESTE DE RESOLUÇÃO DE PÔSTERES (POSTER REPOSITORY) ===")
        filmes.forEach { filme ->
            val result = repository.obterPoster(filme, forceRefresh = true)
            println("• ${filme.titulo}")
            println("  - Fonte: ${result.fonte}")
            println("  - URL: ${result.url ?: "NENHUMA (Usará placeholder ic_claquete_placeholder.xml)"}")
            assertNotNull("Resultado não deve ser nulo", result)
        }
    }
}
