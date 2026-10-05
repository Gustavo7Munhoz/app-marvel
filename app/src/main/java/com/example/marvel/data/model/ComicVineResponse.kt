package com.example.marvel.data.model

import com.google.gson.annotations.SerializedName

data class ComicVineResponse<T>(
    @SerializedName("error") val error: String,
    @SerializedName("limit") val limit: Int,
    @SerializedName("offset") val offset: Int,
    @SerializedName("number_of_page_results") val numberOfPageResults: Int,
    @SerializedName("number_of_total_results") val numberOfTotalResults: Int,
    @SerializedName("status_code") val statusCode: Int,
    @SerializedName("results") val results: T
)
