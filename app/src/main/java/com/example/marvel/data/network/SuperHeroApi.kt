package com.example.marvel.data.network

import com.example.marvel.BuildConfig
import com.example.marvel.data.model.superhero.SuperHeroSearchResponse
import retrofit2.http.GET
import retrofit2.http.Path

interface SuperHeroApi {
    // A API do SuperHero usa o token direto na URL: /api/access-token/search/name
    @GET("{token}/search/{name}")
    suspend fun searchCharacterStats(
        @Path("token") token: String = BuildConfig.SUPERHERO_API_KEY,
        @Path("name") name: String
    ): SuperHeroSearchResponse
}
