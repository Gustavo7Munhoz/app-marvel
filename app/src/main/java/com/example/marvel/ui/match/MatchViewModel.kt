package com.example.marvel.ui.match

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.marvel.domain.model.Character
import com.example.marvel.domain.repository.MarvelRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.random.Random

sealed class MatchUiState {
    object Input : MatchUiState()
    object Scanning : MatchUiState()
    data class Result(val character: Character) : MatchUiState()
    data class Error(val message: String) : MatchUiState()
}

@HiltViewModel
class MatchViewModel @Inject constructor(
    private val repository: MarvelRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<MatchUiState>(MatchUiState.Input)
    val uiState: StateFlow<MatchUiState> = _uiState.asStateFlow()

    fun initiateScan(userName: String) {
        if (userName.isBlank()) return
        
        _uiState.value = MatchUiState.Scanning
        
        viewModelScope.launch {
            // Fake scan delay for cool UI effect
            delay(2500)
            
            // Randomly pick a character
            val offset = Random.nextInt(0, 100)
            val result = repository.getCharacters(limit = 1, offset = offset)
            
            if (result.isSuccess) {
                val chars = result.getOrDefault(emptyList())
                if (chars.isNotEmpty()) {
                    _uiState.value = MatchUiState.Result(chars.first())
                } else {
                    _uiState.value = MatchUiState.Error("Nenhum vínculo encontrado no banco de dados.")
                }
            } else {
                _uiState.value = MatchUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }
    
    fun reset() {
        _uiState.value = MatchUiState.Input
    }
}
