package com.example.marvel.ui.dossier

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

sealed class DossierUiState {
    object Loading : DossierUiState()
    data class Success(val character: Character) : DossierUiState()
    data class Error(val message: String) : DossierUiState()
}

@HiltViewModel
class DossierViewModel @Inject constructor(
    private val repository: MarvelRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<DossierUiState>(DossierUiState.Loading)
    val uiState: StateFlow<DossierUiState> = _uiState.asStateFlow()

    fun loadCharacter(characterId: String) {
        viewModelScope.launch {
            _uiState.value = DossierUiState.Loading
            val result = repository.getCharacterDetails(characterId)
            if (result.isSuccess) {
                _uiState.value = DossierUiState.Success(result.getOrNull()!!)
            } else {
                _uiState.value = DossierUiState.Error(result.exceptionOrNull()?.message ?: "Erro desconhecido ao acessar registros.")
            }
        }
    }
}
