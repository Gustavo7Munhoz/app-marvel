package com.example.marvel.domain.repository

import com.example.marvel.domain.model.Character
import com.example.marvel.data.model.superhero.SuperHeroDto
import com.example.marvel.data.model.ObjectDto

interface MarvelRepository {
    suspend fun getCharacters(limit: Int, offset: Int): Result<List<Character>>
    suspend fun getCharactersByTeam(teamName: String): Result<List<Character>>
    suspend fun getCharacterDetails(characterId: String): Result<Character>
    suspend fun searchCharacters(query: String): Result<List<Character>>

    // SuperHero API — stats de combate
    suspend fun getCharacterStats(name: String): Result<SuperHeroDto>

    // Comic Vine Objects — Joias do Infinito
    suspend fun getInfinityStones(): Result<List<ObjectDto>>
}
