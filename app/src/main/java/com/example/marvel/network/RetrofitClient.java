package com.example.marvel.network;

import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * Cliente Singleton do Retrofit para acesso aos dados da API REST.
 */
public class RetrofitClient {
    private static final String BASE_URL = "https://gateway.marvel.com/v1/public/";
    private static Retrofit retrofit = null;

    public static MarvelApiService getService() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit.create(MarvelApiService.class);
    }
}
