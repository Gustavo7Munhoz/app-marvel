package com.example.marvel.ui.database

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

sealed class DatabaseUiState {
    object Loading : DatabaseUiState()
    data class Success(val characters: List<Character>) : DatabaseUiState()
    data class Error(val message: String) : DatabaseUiState()
}

@HiltViewModel
class DatabaseViewModel @Inject constructor(
    private val repository: MarvelRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<DatabaseUiState>(DatabaseUiState.Loading)
    val uiState: StateFlow<DatabaseUiState> = _uiState.asStateFlow()

    init {
        loadCharacters()
    }

    fun loadCharacters() {
        _uiState.value = DatabaseUiState.Loading
        viewModelScope.launch {
            val result = repository.getCharacters(limit = 50, offset = 0)
            if (result.isSuccess) {
                _uiState.value = DatabaseUiState.Success(result.getOrDefault(emptyList()))
            } else {
                _uiState.value = DatabaseUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }

    fun searchCharacters(query: String) {
        if (query.isBlank()) {
            loadCharacters()
            return
        }
        
        _uiState.value = DatabaseUiState.Loading
        viewModelScope.launch {
            val result = repository.searchCharacters(query)
            if (result.isSuccess) {
                _uiState.value = DatabaseUiState.Success(result.getOrDefault(emptyList()))
            } else {
                _uiState.value = DatabaseUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }
}
