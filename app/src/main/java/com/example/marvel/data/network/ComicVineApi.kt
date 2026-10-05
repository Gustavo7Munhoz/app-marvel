package com.example.marvel.data.network

import com.example.marvel.BuildConfig
import com.example.marvel.data.model.CharacterDto
import com.example.marvel.data.model.ComicVineResponse
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface ComicVineApi {

    @GET("characters")
    suspend fun getCharacters(
        @Query("api_key") apiKey: String = BuildConfig.COMIC_VINE_API_KEY,
        @Query("format") format: String = "json",
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0,
        @Query("sort") sort: String = "name:asc",
        @Query("filter") filter: String? = null
    ): ComicVineResponse<List<CharacterDto>>

    @GET("character/{id}")
    suspend fun getCharacterDetails(
        @Path("id") characterId: String,
        @Query("api_key") apiKey: String = BuildConfig.COMIC_VINE_API_KEY,
        @Query("format") format: String = "json"
    ): ComicVineResponse<CharacterDto>

    @GET("issues")
    suspend fun getIssues(
        @Query("api_key") apiKey: String = BuildConfig.COMIC_VINE_API_KEY,
        @Query("format") format: String = "json",
        @Query("filter") filter: String,
        @Query("field_list") fieldList: String = "id,name,image"
    ): ComicVineResponse<List<com.example.marvel.data.model.IssueDto>>

    @GET("object/{id}")
    suspend fun getObject(
        @Path("id") id: String,
        @Query("api_key") apiKey: String = BuildConfig.COMIC_VINE_API_KEY,
        @Query("format") format: String = "json",
        @Query("field_list") fieldList: String = "id,name,deck,description,image"
    ): ComicVineResponse<com.example.marvel.data.model.ObjectDto>

    @GET("objects")
    suspend fun getObjects(
        @Query("api_key") apiKey: String = BuildConfig.COMIC_VINE_API_KEY,
        @Query("format") format: String = "json",
        @Query("filter") filter: String,
        @Query("field_list") fieldList: String = "id,name,deck,description,image",
        @Query("limit") limit: Int = 10
    ): ComicVineResponse<List<com.example.marvel.data.model.ObjectDto>>
}
