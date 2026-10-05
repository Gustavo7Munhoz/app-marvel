package com.example.marvel.di

import com.example.marvel.data.repository.MarvelRepositoryImpl
import com.example.marvel.domain.repository.MarvelRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindMarvelRepository(
        marvelRepositoryImpl: MarvelRepositoryImpl
    ): MarvelRepository
}
