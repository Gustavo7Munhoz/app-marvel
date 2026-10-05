package com.example.marvel.ui.dossier

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.example.marvel.databinding.FragmentDossierBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class DossierFragment : Fragment() {

    private var _binding: FragmentDossierBinding? = null
    private val binding get() = _binding!!

    private val viewModel: DossierViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDossierBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // Simular a passagem de um ID de teste até termos a Dashboard pronta.
        // Id 1440 = Wolverine na Comic Vine
        val characterId = arguments?.getString("characterId") ?: "1440" 
        
        setupObservers()
        viewModel.loadCharacter(characterId)
    }

    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    when (state) {
                        is DossierUiState.Loading -> {
                            binding.progressBar.visibility = View.VISIBLE
                            binding.contentScrollView.visibility = View.GONE
                        }
                        is DossierUiState.Success -> {
                            binding.progressBar.visibility = View.GONE
                            binding.contentScrollView.visibility = View.VISIBLE
                            
                            val char = state.character
                            binding.tvCharacterName.text = char.name.uppercase()
                            binding.tvRealName.text = char.realName.ifEmpty { "CLASSIFIED" }
                            binding.tvOrigin.text = char.origin.ifEmpty { "UNKNOWN" }
                            binding.tvGender.text = char.gender.ifEmpty { "UNKNOWN" }
                            
                            // O usuário solicitou um resumo básico (deck) em vez do artigo wiki gigante (description)
                            val summary = if (char.deck.isNotBlank() && char.deck != "No records available.") {
                                char.deck
                            } else {
                                // Fallback para uma versão bem mais encurtada
                                val htmlText = androidx.core.text.HtmlCompat.fromHtml(
                                    char.description,
                                    androidx.core.text.HtmlCompat.FROM_HTML_MODE_COMPACT
                                ).toString().trim()
                                
                                val firstDotIndex = htmlText.indexOf('.')
                                if (firstDotIndex in 10..150) {
                                    htmlText.substring(0, firstDotIndex + 1)
                                } else if (htmlText.length > 120) {
                                    htmlText.substring(0, 120) + "..."
                                } else {
                                    htmlText
                                }
                            }
                            binding.tvHistory.text = summary
                            
                            Glide.with(this@DossierFragment)
                                .load(char.imageUrl)
                                .diskCacheStrategy(DiskCacheStrategy.ALL)
                                .placeholder(android.R.color.darker_gray)
                                .error(android.R.color.holo_red_dark)
                                .into(binding.ivCharacterPhoto)
                                
                            val comicAdapter = ComicAdapter(char.comics)
                            binding.rvComics.adapter = comicAdapter
                        }
                        is DossierUiState.Error -> {
                            binding.progressBar.visibility = View.GONE
                            Toast.makeText(context, "Erro de acesso S.H.I.E.L.D.: ${state.message}", Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
