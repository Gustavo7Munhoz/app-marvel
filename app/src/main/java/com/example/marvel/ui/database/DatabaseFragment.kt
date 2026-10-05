package com.example.marvel.ui.database

import android.os.Bundle
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.GridLayoutManager
import com.example.marvel.R
import com.example.marvel.databinding.FragmentDatabaseBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class DatabaseFragment : Fragment() {
    private var _binding: FragmentDatabaseBinding? = null
    private val binding get() = _binding!!

    private val viewModel: DatabaseViewModel by viewModels()
    private lateinit var adapter: CharacterAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDatabaseBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupRecyclerView()
        setupSearch()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        adapter = CharacterAdapter { character ->
            // Ao clicar num card, vai pro Dossier
            val bundle = Bundle().apply { putString("characterId", character.id.toString()) }
            findNavController().navigate(R.id.dossierFragment, bundle)
        }
        
        binding.rvCharacters.layoutManager = GridLayoutManager(requireContext(), 2)
        binding.rvCharacters.adapter = adapter
    }

    private fun setupSearch() {
        binding.etSearch.setOnEditorActionListener { _, actionId, event ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH ||
                (event?.keyCode == KeyEvent.KEYCODE_ENTER && event.action == KeyEvent.ACTION_DOWN)
            ) {
                val query = binding.etSearch.text?.toString()?.trim() ?: ""
                viewModel.searchCharacters(query)
                true
            } else false
        }
    }

    private fun observeViewModel() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    when (state) {
                        is DatabaseUiState.Loading -> {
                            binding.progressBar.visibility = View.VISIBLE
                            binding.rvCharacters.visibility = View.GONE
                            binding.tvMessage.visibility = View.GONE
                        }
                        is DatabaseUiState.Success -> {
                            binding.progressBar.visibility = View.GONE
                            if (state.characters.isEmpty()) {
                                binding.tvMessage.text = "No records found."
                                binding.tvMessage.visibility = View.VISIBLE
                                binding.rvCharacters.visibility = View.GONE
                            } else {
                                binding.tvMessage.visibility = View.GONE
                                binding.rvCharacters.visibility = View.VISIBLE
                                adapter.submitList(state.characters)
                            }
                        }
                        is DatabaseUiState.Error -> {
                            binding.progressBar.visibility = View.GONE
                            binding.rvCharacters.visibility = View.GONE
                            binding.tvMessage.text = "Error accessing S.H.I.E.L.D. database:\n${state.message}"
                            binding.tvMessage.visibility = View.VISIBLE
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
