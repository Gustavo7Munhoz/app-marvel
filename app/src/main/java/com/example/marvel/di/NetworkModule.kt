package com.example.marvel.di

import com.example.marvel.BuildConfig
import com.example.marvel.data.network.ComicVineApi
import com.example.marvel.data.network.SuperHeroApi
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Named
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    private const val COMIC_VINE_BASE_URL = "https://comicvine.gamespot.com/api/"
    private const val SUPERHERO_BASE_URL = "https://superheroapi.com/api/"

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                    else HttpLoggingInterceptor.Level.NONE
        }
        return OkHttpClient.Builder()
            .addInterceptor { chain ->
                val original = chain.request()
                // A API da Comic Vine exige um User-Agent válido
                val request = original.newBuilder()
                    .header("User-Agent", "MarvelShieldCommandCenter/1.0 (Android)")
                    .method(original.method, original.body)
                    .build()
                chain.proceed(request)
            }
            .addInterceptor(logging)
            .readTimeout(30, TimeUnit.SECONDS)
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    // COMIC VINE RETROFIT
    @Provides
    @Singleton
    @Named("ComicVineRetrofit")
    fun provideComicVineRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(COMIC_VINE_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideComicVineApi(@Named("ComicVineRetrofit") retrofit: Retrofit): ComicVineApi {
        return retrofit.create(ComicVineApi::class.java)
    }

    // SUPERHERO RETROFIT
    @Provides
    @Singleton
    @Named("SuperHeroRetrofit")
    fun provideSuperHeroRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(SUPERHERO_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideSuperHeroApi(@Named("SuperHeroRetrofit") retrofit: Retrofit): SuperHeroApi {
        return retrofit.create(SuperHeroApi::class.java)
    }
}
