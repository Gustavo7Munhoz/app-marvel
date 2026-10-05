package com.example.marvel

import com.example.marvel.ui.operacoes.OperacoesUiState
import com.example.marvel.ui.operacoes.OperacoesViewModel
import org.junit.Assert.*
import org.junit.Test
import java.time.LocalDate

class OperacoesFilterTest {

    @Test
    fun testCarregarOperacoes_filtragemEOrdenacao() {
        val viewModel = OperacoesViewModel()
        val state = viewModel.uiState.value
        assertTrue(state is OperacoesUiState.Success)
        val filmes = (state as OperacoesUiState.Success).filmes

        println("=== LISTA DE OPERAÇÕES FILTRADAS (${LocalDate.now()}) ===")
        filmes.forEachIndexed { i, f ->
            println("${i + 1}. [${f.dataFormatada}] ${f.titulo} | Destaque: ${f.isDestaque} | Contador: ${f.contadorRegressivo} | Categoria: ${f.categoria}")
        }

        // Verifica que todos os itens na lista têm data >= hoje ou são "A definir"
        val hoje = LocalDate.now()
        for (filme in filmes) {
            if (filme.dataParsed != null) {
                assertFalse("Não deve conter filmes anteriores a hoje ($hoje): ${filme.titulo}", filme.dataParsed.isBefore(hoje))
            }
        }

        // Verifica que o primeiro item é destaque com contador
        if (filmes.isNotEmpty()) {
            val primeiro = filmes.first()
            assertTrue(primeiro.isDestaque)
            assertNotNull(primeiro.contadorRegressivo)
            println("PRÓXIMO LANÇAMENTO: ${primeiro.titulo} -> ${primeiro.contadorRegressivo}")
        }

        // Itens sem data devem estar no final
        var encontrouSemData = false
        for (filme in filmes) {
            if (filme.dataParsed == null) {
                encontrouSemData = true
            } else if (encontrouSemData) {
                fail("Item com data (${filme.titulo}) apareceu após item 'A definir'!")
            }
        }
    }
}
