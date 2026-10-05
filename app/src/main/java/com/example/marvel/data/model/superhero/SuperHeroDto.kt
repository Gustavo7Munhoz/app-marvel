package com.example.marvel.data.model.superhero

import com.google.gson.annotations.SerializedName

data class SuperHeroSearchResponse(
    @SerializedName("response") val response: String,
    @SerializedName("results") val results: List<SuperHeroDto>?
)

data class SuperHeroDto(
    @SerializedName("id") val id: String,
    @SerializedName("name") val name: String,
    @SerializedName("powerstats") val powerstats: PowerStatsDto,
    @SerializedName("biography") val biography: BiographyDto?,
    @SerializedName("image") val image: SuperHeroImageDto?
)

data class SuperHeroImageDto(
    @SerializedName("url") val url: String?
)

data class BiographyDto(
    @SerializedName("publisher") val publisher: String?
)

data class PowerStatsDto(
    @SerializedName("intelligence") val intelligence: String,
    @SerializedName("strength") val strength: String,
    @SerializedName("speed") val speed: String,
    @SerializedName("durability") val durability: String,
    @SerializedName("power") val power: String,
    @SerializedName("combat") val combat: String
)
