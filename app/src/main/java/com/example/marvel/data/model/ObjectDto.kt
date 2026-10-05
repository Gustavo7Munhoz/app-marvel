package com.example.marvel.data.model

import com.google.gson.annotations.SerializedName

data class ObjectDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String?,
    @SerializedName("deck") val deck: String?,
    @SerializedName("description") val description: String?,
    @SerializedName("image") val image: ImageDto?
)
