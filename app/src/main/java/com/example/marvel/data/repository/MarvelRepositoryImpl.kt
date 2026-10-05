package com.example.marvel.data.repository

import com.example.marvel.data.model.ObjectDto
import com.example.marvel.data.network.ComicVineApi
import com.example.marvel.data.network.SuperHeroApi
import com.example.marvel.data.model.superhero.SuperHeroDto
import com.example.marvel.domain.model.Character
import com.example.marvel.domain.repository.MarvelRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.withContext
import javax.inject.Inject

// Garante que URLs de imagem usem sempre HTTPS (Comic Vine às vezes retorna HTTP)
private fun String?.toHttps(): String =
    this?.replace("http://", "https://") ?: ""

class MarvelRepositoryImpl @Inject constructor(
    private val api: ComicVineApi,
    private val superHeroApi: SuperHeroApi
) : MarvelRepository {

    override suspend fun getInfinityStones(): Result<List<ObjectDto>> {
        return withContext(Dispatchers.IO) {
            try {
                // A API da Comic Vine requer o prefixo tipo para 'object', mas usando 'objects' 
                // com filtro de múltiplos IDs funciona numa única chamada e evita rate limits!
                val filterQuery = "id:55644|55645|57126|57127|57128|57129"
                val response = api.getObjects(filter = filterQuery)
                
                if (response.error == "OK" && response.results != null) {
                    Result.success(response.results)
                } else {
                    Result.failure(Exception("Nenhuma joia encontrada. Status: ${response.error}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun getCharacters(limit: Int, offset: Int): Result<List<Character>> {
        return withContext(Dispatchers.IO) {
            try {
                // publisher:43 is Marvel Comics in Comic Vine
                val response = api.getCharacters(limit = limit, offset = offset, filter = "publisher:43")
                if (response.error == "OK") {
                    val characters = response.results.map { dto ->
                        Character(
                            id = dto.id,
                            name = dto.name ?: "Unknown",
                            realName = dto.realName ?: "Classified",
                            aliases = dto.aliases ?: "",
                            deck = dto.deck ?: "No records available.",
                            description = dto.description ?: "",
                            imageUrl = (dto.image?.mediumUrl ?: dto.image?.screenUrl).toHttps(),
                            publisher = dto.publisher?.name ?: "Unknown",
                            origin = dto.origin?.name ?: "Unknown",
                            gender = when (dto.gender) {
                                1 -> "Male"
                                2 -> "Female"
                                3 -> "Other"
                                else -> "Unspecified"
                            }
                        )
                    }
                    Result.success(characters)
                } else {
                    Result.failure(Exception("API Error: ${response.error}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun getCharactersByTeam(teamName: String): Result<List<Character>> {
        return withContext(Dispatchers.IO) {
            try {
                // Hardcoded core members for the major Marvel teams
                val teamIds = when (teamName.lowercase()) {
                    "avengers" -> "1455|1442|2268|2267|3200|1475"
                    "quarteto fantástico" -> "2151|2190|2120|2114"
                    "guardiões da galáxia" -> "10957|6806|6807|32814|24341"
                    "thunderbolts" -> "3278|3281|3279"
                    "xman" -> "1440|1459|1444|3552|61243"
                    "eternos" -> "13967|2118|13822"
                    else -> ""
                }

                if (teamIds.isEmpty()) return@withContext Result.success(emptyList())

                // Fetch characters matching these exact IDs
                val response = api.getCharacters(filter = "id:$teamIds", limit = 50)
                if (response.error == "OK") {
                    val characters = response.results.map { dto ->
                        Character(
                            id = dto.id,
                            name = dto.name ?: "Unknown",
                            realName = dto.realName ?: "Classified",
                            aliases = dto.aliases ?: "",
                            deck = dto.deck ?: "No records available.",
                            description = dto.description ?: "",
                            imageUrl = (dto.image?.mediumUrl ?: dto.image?.screenUrl).toHttps(),
                            publisher = dto.publisher?.name ?: "Unknown",
                            origin = dto.origin?.name ?: "Unknown",
                            gender = when (dto.gender) {
                                1 -> "Male"
                                2 -> "Female"
                                3 -> "Other"
                                else -> "Unspecified"
                            }
                        )
                    }
                    Result.success(characters)
                } else {
                    Result.failure(Exception("API Error: ${response.error}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun getCharacterDetails(characterId: String): Result<Character> {
        return withContext(Dispatchers.IO) {
            try {
                val response = api.getCharacterDetails(characterId = "4005-$characterId") // Comic Vine requires 4005- prefix for characters in details route
                if (response.error == "OK") {
                    val dto = response.results
                    
                    val comicsList = mutableListOf<com.example.marvel.domain.model.Comic>()
                    val issueCredits = dto.issueCredits ?: emptyList()
                    
                    if (issueCredits.isNotEmpty()) {
                        // Limitar a 15 para não dar timeout ou url too long
                        val topIssues = issueCredits.take(15)
                        val filterIds = topIssues.joinToString("|") { it.id.toString() }
                        try {
                            val issuesResponse = api.getIssues(filter = "id:$filterIds")
                            if (issuesResponse.error == "OK") {
                                issuesResponse.results.forEach { issueDto ->
                                    val fallbackName = topIssues.find { it.id == issueDto.id }?.name ?: "UNKNOWN ISSUE"
                                    val name = issueDto.name ?: fallbackName
                                    val image = (issueDto.image?.mediumUrl ?: issueDto.image?.screenUrl).toHttps()
                                    comicsList.add(com.example.marvel.domain.model.Comic(issueDto.id, name, image))
                                }
                            }
                        } catch (e: Exception) {
                            // Se falhar os quadrinhos, continua carregando o personagem normal
                        }
                    }

                    val character = Character(
                        id = dto.id,
                        name = dto.name ?: "Unknown",
                        realName = dto.realName ?: "Classified",
                        aliases = dto.aliases ?: "",
                        deck = dto.deck ?: "No records available.",
                        description = dto.description ?: "",
                        imageUrl = (dto.image?.mediumUrl ?: dto.image?.screenUrl).toHttps(),
                        publisher = dto.publisher?.name ?: "Unknown",
                        origin = dto.origin?.name ?: "Unknown",
                        gender = when (dto.gender) {
                            1 -> "Male"
                            2 -> "Female"
                            3 -> "Other"
                            else -> "Unspecified"
                        },
                        comics = comicsList
                    )
                    Result.success(character)
                } else {
                    Result.failure(Exception("API Error: ${response.error}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun searchCharacters(query: String): Result<List<Character>> {
        return withContext(Dispatchers.IO) {
            try {
                // Filter format field:name:value and publisher:43 (Marvel)
                val response = api.getCharacters(filter = "name:$query,publisher:43")
                if (response.error == "OK") {
                    val characters = response.results.map { dto ->
                        Character(
                            id = dto.id,
                            name = dto.name ?: "Unknown",
                            realName = dto.realName ?: "Classified",
                            aliases = dto.aliases ?: "",
                            deck = dto.deck ?: "No records available.",
                            description = dto.description ?: "",
                            imageUrl = (dto.image?.mediumUrl ?: dto.image?.screenUrl).toHttps(),
                            publisher = dto.publisher?.name ?: "Unknown",
                            origin = dto.origin?.name ?: "Unknown",
                            gender = when (dto.gender) {
                                1 -> "Male"
                                2 -> "Female"
                                3 -> "Other"
                                else -> "Unspecified"
                            }
                        )
                    }
                    Result.success(characters)
                } else {
                    Result.failure(Exception("API Error: ${response.error}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    override suspend fun getCharacterStats(name: String): Result<SuperHeroDto> {
        return withContext(Dispatchers.IO) {
            try {
                val response = superHeroApi.searchCharacterStats(name = name)
                if (response.response == "success" && !response.results.isNullOrEmpty()) {
                    // Filtra para garantir que seja da Marvel (evitando Lex Luthor quando procura Thor, etc)
                    val marvelHero = response.results.firstOrNull { 
                        it.biography?.publisher?.contains("Marvel", ignoreCase = true) == true
                    }
                    
                    if (marvelHero != null) {
                        Result.success(marvelHero)
                    } else {
                        Result.failure(Exception("Character found, but is not from Marvel Comics."))
                    }
                } else {
                    Result.failure(Exception("Character stats not found for: $name"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}
