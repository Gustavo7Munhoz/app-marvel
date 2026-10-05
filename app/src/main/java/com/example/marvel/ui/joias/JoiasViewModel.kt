package com.example.marvel.ui.joias

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.marvel.data.model.ObjectDto
import com.example.marvel.domain.repository.MarvelRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class JoiasUiState {
    object Loading : JoiasUiState()
    data class Success(val gems: List<ObjectDto>) : JoiasUiState()
    data class Error(val message: String) : JoiasUiState()
}

@HiltViewModel
class JoiasViewModel @Inject constructor(
    private val repository: MarvelRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<JoiasUiState>(JoiasUiState.Loading)
    val uiState: StateFlow<JoiasUiState> = _uiState

    init {
        loadStones()
    }

    private fun loadStones() {
        viewModelScope.launch {
            _uiState.value = JoiasUiState.Loading
            repository.getInfinityStones().fold(
                onSuccess = { stones ->
                    _uiState.value = JoiasUiState.Success(stones)
                },
                onFailure = { error ->
                    _uiState.value = JoiasUiState.Error(error.message ?: "Erro desconhecido")
                }
            )
        }
    }
}
