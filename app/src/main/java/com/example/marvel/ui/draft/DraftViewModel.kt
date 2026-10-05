package com.example.marvel.ui.draft

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

sealed class DraftUiState {
    object Loading : DraftUiState()
    data class Success(val characters: List<Character>) : DraftUiState()
    data class Error(val message: String) : DraftUiState()
}

@HiltViewModel
class DraftViewModel @Inject constructor(
    private val repository: MarvelRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<DraftUiState>(DraftUiState.Loading)
    val uiState: StateFlow<DraftUiState> = _uiState.asStateFlow()
    
    // Lista de personagens draftados (máximo 5)
    private val _draftedCharacters = MutableStateFlow<List<Character>>(emptyList())
    val draftedCharacters: StateFlow<List<Character>> = _draftedCharacters.asStateFlow()

    init {
        loadCharacters()
    }

    fun loadCharacters() {
        _uiState.value = DraftUiState.Loading
        viewModelScope.launch {
            val result = repository.getCharacters(limit = 50, offset = 0)
            if (result.isSuccess) {
                _uiState.value = DraftUiState.Success(result.getOrDefault(emptyList()))
            } else {
                _uiState.value = DraftUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }

    fun searchCharacters(query: String) {
        if (query.isBlank()) {
            loadCharacters()
            return
        }
        
        _uiState.value = DraftUiState.Loading
        viewModelScope.launch {
            val result = repository.searchCharacters(query)
            if (result.isSuccess) {
                _uiState.value = DraftUiState.Success(result.getOrDefault(emptyList()))
            } else {
                _uiState.value = DraftUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }

    fun loadCharactersByTeam(teamName: String) {
        _uiState.value = DraftUiState.Loading
        viewModelScope.launch {
            val result = repository.getCharactersByTeam(teamName)
            if (result.isSuccess) {
                _uiState.value = DraftUiState.Success(result.getOrDefault(emptyList()))
            } else {
                _uiState.value = DraftUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }
    
    fun toggleDraft(character: Character) {
        val currentList = _draftedCharacters.value.toMutableList()
        if (currentList.any { it.id == character.id }) {
            // Se já está no time, remove
            currentList.removeAll { it.id == character.id }
        } else {
            // Se não está no time, adiciona se tiver espaço
            if (currentList.size < 5) {
                currentList.add(character)
            }
        }
        _draftedCharacters.value = currentList
    }
    
    fun removeDraftAt(index: Int) {
        val currentList = _draftedCharacters.value.toMutableList()
        if (index in currentList.indices) {
            currentList.removeAt(index)
            _draftedCharacters.value = currentList
        }
    }
}
