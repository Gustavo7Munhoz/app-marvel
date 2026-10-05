package com.example.marvel.ui.intel

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
import com.example.marvel.databinding.FragmentArchiveBinding
import com.example.marvel.ui.database.CharacterAdapter
import com.example.marvel.ui.home.HomeUiState
import com.example.marvel.ui.home.HomeViewModel
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class ArchiveFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enterTransition = com.google.android.material.transition.MaterialFadeThrough()
        exitTransition = com.google.android.material.transition.MaterialFadeThrough()
    }

    private var _binding: FragmentArchiveBinding? = null
    private val binding get() = _binding!!

    private val viewModel: HomeViewModel by viewModels()
    private lateinit var adapter: CharacterAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentArchiveBinding.inflate(inflater, container, false)
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
            val bundle = Bundle().apply { putString("characterId", character.id.toString()) }
            findNavController().navigate(R.id.action_archiveFragment_to_dossierFragment, bundle)
        }
        binding.rvCharacters.layoutManager = GridLayoutManager(requireContext(), 2)
        val spacing = (8 * resources.displayMetrics.density).toInt()
        binding.rvCharacters.addItemDecoration(object : androidx.recyclerview.widget.RecyclerView.ItemDecoration() {
            override fun getItemOffsets(
                outRect: android.graphics.Rect,
                view: View,
                parent: androidx.recyclerview.widget.RecyclerView,
                state: androidx.recyclerview.widget.RecyclerView.State
            ) {
                outRect.left = spacing / 2
                outRect.right = spacing / 2
                outRect.top = spacing / 2
                outRect.bottom = spacing / 2
            }
        })
        binding.rvCharacters.adapter = adapter
    }

    private fun setupSearch() {
        binding.btnFilter.setOnClickListener {
            val bottomSheetDialog = com.google.android.material.bottomsheet.BottomSheetDialog(requireContext())
            val view = layoutInflater.inflate(R.layout.dialog_team_filter, null)
            bottomSheetDialog.setContentView(view)
            (view.parent as? View)?.setBackgroundColor(android.graphics.Color.TRANSPARENT)

            val optionsContainer = view.findViewById<android.widget.LinearLayout>(R.id.optionsContainer)
            val btnClearFilter = view.findViewById<View>(R.id.btnClearFilter)

            val teams = arrayOf("Avengers", "Quarteto Fantástico", "Guardiões da Galáxia", "Thunderbolts", "XMan", "Eternos")
            teams.forEach { team ->
                val tv = layoutInflater.inflate(R.layout.item_filter_team, optionsContainer, false) as android.widget.TextView
                tv.text = team
                tv.setOnClickListener {
                    viewModel.loadCharactersByTeam(team)
                    bottomSheetDialog.dismiss()
                }
                optionsContainer.addView(tv)
                val divider = View(requireContext()).apply {
                    layoutParams = android.widget.LinearLayout.LayoutParams(android.widget.LinearLayout.LayoutParams.MATCH_PARENT, 1)
                    setBackgroundColor(androidx.core.content.ContextCompat.getColor(context, R.color.shield_light_gray))
                }
                optionsContainer.addView(divider)
            }
            btnClearFilter.setOnClickListener {
                binding.etSearch.text?.clear()
                viewModel.loadCharacters()
                bottomSheetDialog.dismiss()
            }
            bottomSheetDialog.show()
        }

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
                        is HomeUiState.Loading -> {
                            binding.progressBar.visibility = View.VISIBLE
                            binding.rvCharacters.visibility = View.GONE
                            binding.tvMessage.visibility = View.GONE
                        }
                        is HomeUiState.Success -> {
                            binding.progressBar.visibility = View.GONE
                            if (state.characters.isEmpty()) {
                                binding.tvMessage.text = "NENHUM OPERATIVO ENCONTRADO."
                                binding.tvMessage.visibility = View.VISIBLE
                                binding.rvCharacters.visibility = View.GONE
                            } else {
                                binding.tvMessage.visibility = View.GONE
                                binding.rvCharacters.visibility = View.VISIBLE
                                adapter.submitList(state.characters)
                            }
                        }
                        is HomeUiState.Error -> {
                            binding.progressBar.visibility = View.GONE
                            binding.rvCharacters.visibility = View.GONE
                            binding.tvMessage.text = "ERRO DO SISTEMA:\n${state.message}"
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
