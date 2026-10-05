package com.example.marvel.network;

import java.util.List;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Query;

/**
 * Interface Retrofit para consumo da API REST de Dossiês Marvel/S.H.I.E.L.D.
 */
public interface MarvelApiService {
    @GET("characters")
    Call<List<CharacterModel>> getCharacters(
        @Query("limit") int limit,
        @Query("apikey") String apiKey
    );
}
