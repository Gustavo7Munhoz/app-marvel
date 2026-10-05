package com.example.marvel.ui.battle

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.marvel.data.model.superhero.SuperHeroDto
import com.example.marvel.domain.repository.MarvelRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class BattleUiState {
    object Idle : BattleUiState()
    object Loading : BattleUiState()
    data class Success(
        val fighter1: SuperHeroDto,
        val fighter2: SuperHeroDto,
        val imageUrl1: String? = null,
        val imageUrl2: String? = null
    ) : BattleUiState()
    data class Error(val message: String) : BattleUiState()
}

@HiltViewModel
class BattleViewModel @Inject constructor(
    private val repository: MarvelRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<BattleUiState>(BattleUiState.Idle)
    val uiState: StateFlow<BattleUiState> = _uiState.asStateFlow()

    fun simulateBattle(name1: String, name2: String) {
        if (name1.isBlank() || name2.isBlank()) {
            _uiState.value = BattleUiState.Error("Digite o nome dos 2 combatentes para comparar.")
            return
        }

        _uiState.value = BattleUiState.Loading
        viewModelScope.launch {
            val result1 = repository.getCharacterStats(name1)
            val result2 = repository.getCharacterStats(name2)

            if (result1.isSuccess && result2.isSuccess) {
                val f1 = result1.getOrThrow()
                val f2 = result2.getOrThrow()

                // Busca imagens seguras no ComicVine como fallback preferencial às URLs bloqueadas do SuperHeroDB
                val cvImg1 = try {
                    repository.searchCharacters(f1.name).getOrNull()?.firstOrNull()?.imageUrl
                } catch (_: Exception) {
                    null
                }

                val cvImg2 = try {
                    repository.searchCharacters(f2.name).getOrNull()?.firstOrNull()?.imageUrl
                } catch (_: Exception) {
                    null
                }

                _uiState.value = BattleUiState.Success(
                    fighter1 = f1,
                    fighter2 = f2,
                    imageUrl1 = cvImg1 ?: f1.image?.url,
                    imageUrl2 = cvImg2 ?: f2.image?.url
                )
            } else {
                val errorMsg = if (result1.isFailure) {
                    "Combatente 1 não encontrado no banco de dados."
                } else {
                    "Combatente 2 não encontrado no banco de dados."
                }
                _uiState.value = BattleUiState.Error(errorMsg)
            }
        }
    }
}
