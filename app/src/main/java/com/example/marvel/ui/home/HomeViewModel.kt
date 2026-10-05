package com.example.marvel.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.marvel.domain.model.Character
import com.example.marvel.domain.repository.MarvelRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class HomeUiState {
    object Loading : HomeUiState()
    data class Success(val characters: List<Character>) : HomeUiState()
    data class Error(val message: String) : HomeUiState()
}

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: MarvelRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<HomeUiState>(HomeUiState.Loading)
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadCharacters()
    }

    fun loadCharacters() {
        _uiState.value = HomeUiState.Loading
        viewModelScope.launch {
                val result = repository.getCharacters(limit = 50, offset = 0)
            if (result.isSuccess) {
                _uiState.value = HomeUiState.Success(result.getOrDefault(emptyList()))
            } else {
                _uiState.value = HomeUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }

    fun searchCharacters(query: String) {
        if (query.isBlank()) {
            loadCharacters()
            return
        }
        
        _uiState.value = HomeUiState.Loading
        viewModelScope.launch {
            val result = repository.searchCharacters(query)
            if (result.isSuccess) {
                _uiState.value = HomeUiState.Success(result.getOrDefault(emptyList()))
            } else {
                _uiState.value = HomeUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }

    fun loadCharactersByTeam(teamName: String) {
        _uiState.value = HomeUiState.Loading
        viewModelScope.launch {
            val result = repository.getCharactersByTeam(teamName)
            if (result.isSuccess) {
                _uiState.value = HomeUiState.Success(result.getOrDefault(emptyList()))
            } else {
                _uiState.value = HomeUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }
}
