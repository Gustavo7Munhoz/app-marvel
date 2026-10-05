package com.example.marvel

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.marvel.adapter.FilmeAdapter
import com.example.marvel.databinding.FragmentHomeBinding
import com.example.marvel.game.TermoGameManager
import com.example.marvel.model.FilmeModel
import com.example.marvel.ui.operacoes.OperacoesUiState
import com.example.marvel.ui.operacoes.OperacoesViewModel
import com.google.android.material.tabs.TabLayout
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class HomeFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enterTransition = com.google.android.material.transition.MaterialFadeThrough()
        exitTransition = com.google.android.material.transition.MaterialFadeThrough()
    }

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    // Mini-game Termo Operativo
    private val termoManager = TermoGameManager("THORS")
    private lateinit var termoGrid: Array<Array<TextView>>

    // ViewModel e Adapter de Operações / Lançamentos
    private val operacoesViewModel: OperacoesViewModel by viewModels()
    private lateinit var filmeAdapter: FilmeAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        if (!hasAnimatedFirstEntry) {
            binding.headerHome.alpha = 0f
            binding.tabOperacoes.alpha = 0f
            binding.chipGroupFiltros.alpha = 0f

            binding.headerHome.animate().alpha(1f).setDuration(400).start()
            binding.tabOperacoes.animate().alpha(1f).setDuration(400).setStartDelay(100).start()
            binding.chipGroupFiltros.animate().alpha(1f).setDuration(400).setStartDelay(150).start()
        }

        setupTabs()
        setupFilmes()
        setupFiltros()
        observeOperacoes()
        setupTermoGame()
    }

    override fun onResume() {
        super.onResume()
        // Atualiza a lista com base na data do aparelho (LocalDate.now()) a cada carregamento da tela
        operacoesViewModel.carregarOperacoes()
    }

    private fun setupTabs() {
        binding.tabOperacoes.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                when (tab?.position) {
                    0 -> {
                        binding.layoutCalendarioOperacoes.visibility = View.VISIBLE
                        binding.layoutTermoOperativo.visibility = View.GONE
                    }
                    1 -> {
                        binding.layoutCalendarioOperacoes.visibility = View.GONE
                        binding.layoutTermoOperativo.visibility = View.VISIBLE
                    }
                }
            }

            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })
    }

    private fun setupFilmes() {
        filmeAdapter = FilmeAdapter(ArrayList())
        binding.rvOperacoes.layoutManager = LinearLayoutManager(requireContext())
        binding.rvOperacoes.adapter = filmeAdapter
        if (!hasAnimatedFirstEntry) {
            val animation = android.view.animation.AnimationUtils.loadLayoutAnimation(
                requireContext(),
                R.anim.layout_anim_cascade
            )
            binding.rvOperacoes.layoutAnimation = animation
        }
    }

    private fun setupFiltros() {
        binding.chipTodos.isChecked = true

        binding.chipGroupFiltros.setOnCheckedStateChangeListener { _, checkedIds ->
            if (checkedIds.isEmpty()) return@setOnCheckedStateChangeListener

            val categoria = when (checkedIds[0]) {
                R.id.chipCinema -> "CINEMA"
                R.id.chipDisneyPlus -> "DISNEY+"
                else -> "TODOS"
            }
            operacoesViewModel.filtrarPorCategoria(categoria)
        }
    }

    private fun observeOperacoes() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                operacoesViewModel.uiState.collect { state ->
                    when (state) {
                        is OperacoesUiState.Success -> {
                            binding.progressBarOperacoes.visibility = if (state.isLoading) View.VISIBLE else View.GONE
                            filmeAdapter.setLista(ArrayList(state.filmes))
                            if (state.isVazio) {
                                binding.rvOperacoes.visibility = View.GONE
                                binding.layoutEmptyOperacoes.visibility = View.VISIBLE
                            } else {
                                binding.rvOperacoes.visibility = View.VISIBLE
                                binding.layoutEmptyOperacoes.visibility = View.GONE
                                if (!hasAnimatedFirstEntry && state.filmes.isNotEmpty()) {
                                    hasAnimatedFirstEntry = true
                                    binding.rvOperacoes.scheduleLayoutAnimation()
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    private fun setupTermoGame() {
        termoGrid = arrayOf(
            arrayOf(binding.cell00, binding.cell01, binding.cell02, binding.cell03, binding.cell04),
            arrayOf(binding.cell10, binding.cell11, binding.cell12, binding.cell13, binding.cell14),
            arrayOf(binding.cell20, binding.cell21, binding.cell22, binding.cell23, binding.cell24),
            arrayOf(binding.cell30, binding.cell31, binding.cell32, binding.cell33, binding.cell34),
            arrayOf(binding.cell40, binding.cell41, binding.cell42, binding.cell43, binding.cell44),
            arrayOf(binding.cell50, binding.cell51, binding.cell52, binding.cell53, binding.cell54)
        )

        binding.btnValidarTermo.setOnClickListener {
            processarTentativaTermo()
        }
    }

    private fun processarTentativaTermo() {
        if (termoManager.isJogoFinalizado) {
            Toast.makeText(requireContext(), "Missão finalizada! Operativo era: ${termoManager.palavraCerta}", Toast.LENGTH_SHORT).show()
            return
        }

        val palpite = binding.etPalpiteTermo.text.toString().trim().uppercase()
        if (palpite.length != 5) {
            Toast.makeText(requireContext(), "Digite exatamente 5 letras!", Toast.LENGTH_SHORT).show()
            return
        }

        val tentativaAtual = termoManager.tentativaAtual
        if (tentativaAtual < termoManager.maxTentativas) {
            val linhaCells = termoGrid[tentativaAtual]
            val acertou = termoManager.validarTentativa(palpite, linhaCells)

            binding.etPalpiteTermo.text.clear()

            if (acertou) {
                binding.tvStatusTermo.text = "★ AUTORIZAÇÃO CONCEDIDA: OPERATIVO ${termoManager.palavraCerta} IDENTIFICADO!"
                binding.tvStatusTermo.setTextColor(resources.getColor(R.color.shield_green_clearance, null))
                Toast.makeText(requireContext(), "Parabéns, Agente! Código decifrado!", Toast.LENGTH_LONG).show()
            } else if (termoManager.isJogoFinalizado) {
                binding.tvStatusTermo.text = "ACESSO NEGADO // OPERATIVO ERA: ${termoManager.palavraCerta}"
                binding.tvStatusTermo.setTextColor(resources.getColor(R.color.shield_red_classified, null))
                Toast.makeText(requireContext(), "Tentativas esgotadas!", Toast.LENGTH_LONG).show()
            } else {
                binding.tvStatusTermo.text = "TENTATIVA ${termoManager.tentativaAtual} DE ${termoManager.maxTentativas} REGISTRADA"
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    companion object {
        var hasAnimatedFirstEntry = false
    }
}
