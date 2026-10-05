package com.example.marvel.domain.model

data class Character(
    val id: Int,
    val name: String,
    val realName: String,
    val aliases: String,
    val deck: String, // Breve descrição
    val description: String, // Descrição completa em HTML
    val imageUrl: String,
    val publisher: String,
    val origin: String,
    val gender: String,
    val comics: List<Comic> = emptyList()
)

data class Comic(
    val id: Int,
    val name: String,
    val imageUrl: String
)
