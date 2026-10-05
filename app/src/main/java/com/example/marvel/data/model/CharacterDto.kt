package com.example.marvel.data.model

import com.google.gson.annotations.SerializedName

data class CharacterDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String?,
    @SerializedName("real_name") val realName: String?,
    @SerializedName("aliases") val aliases: String?,
    @SerializedName("deck") val deck: String?, // Short description
    @SerializedName("description") val description: String?, // HTML long description
    @SerializedName("image") val image: ImageDto?,
    @SerializedName("publisher") val publisher: PublisherDto?,
    @SerializedName("issue_credits") val issueCredits: List<IssueDto>?,
    @SerializedName("origin") val origin: OriginDto?,
    @SerializedName("gender") val gender: Int?
)

data class OriginDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String?
)

data class IssueDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String?,
    @SerializedName("image") val image: ImageDto?
)

data class ImageDto(
    @SerializedName("icon_url") val iconUrl: String?,
    @SerializedName("medium_url") val mediumUrl: String?,
    @SerializedName("screen_url") val screenUrl: String?,
    @SerializedName("original_url") val originalUrl: String?
)

data class PublisherDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String?
)
