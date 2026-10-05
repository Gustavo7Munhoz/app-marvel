package com.example.marvel;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.marvel.adapter.OperacoesAdapter;
import com.example.marvel.viewmodel.OperacoesViewModel;
import com.google.android.material.chip.Chip;
import com.google.android.material.chip.ChipGroup;
import com.google.android.material.tabs.TabLayout;

/**
 * Fragment em Java responsável pela exibição do Calendário de Operações S.H.I.E.L.D.
 * Gerencia a filtragem dinâmica via ChipGroup (iniciando por padrão em FUTUROS)
 * e a renderização com múltiplos ViewTypes via OperacoesAdapter.
 */
public class OperacoesFragment extends Fragment {

    private OperacoesViewModel viewModel;
    private OperacoesAdapter adapter;

    private RecyclerView rvOperacoes;
    private ChipGroup chipGroupFiltros;
    private Chip chipTodos;
    private Chip chipCinema;
    private Chip chipDisneyPlus;

    private View layoutCalendario;
    private View layoutTermo;
    private TabLayout tabOperacoes;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_home, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // 1. Inicializa o ViewModel
        viewModel = new ViewModelProvider(this).get(OperacoesViewModel.class);

        // 2. Mapeia os componentes do layout XML
        inicializarViews(view);

        // 3. Configura o RecyclerView com OperacoesAdapter
        configurarRecyclerView();

        // 4. Configura os ouvintes do ChipGroup (Fase 1)
        configurarChipGroupFiltros();

        // 5. Configura as abas (Calendário de Operações vs Termo Operativo)
        configurarTabs();

        // 6. Observa as mudanças da lista filtrada no ViewModel
        viewModel.getOperacoesFiltradas().observe(getViewLifecycleOwner(), operacoes -> {
            if (adapter != null && operacoes != null) {
                adapter.setLista(operacoes);
            }
        });
    }

    private void inicializarViews(@NonNull View view) {
        rvOperacoes = view.findViewById(R.id.rvOperacoes);
        chipGroupFiltros = view.findViewById(R.id.chipGroupFiltros);
        chipTodos = view.findViewById(R.id.chipTodos);
        chipCinema = view.findViewById(R.id.chipCinema);
        chipDisneyPlus = view.findViewById(R.id.chipDisneyPlus);

        layoutCalendario = view.findViewById(R.id.layoutCalendarioOperacoes);
        layoutTermo = view.findViewById(R.id.layoutTermoOperativo);
        tabOperacoes = view.findViewById(R.id.tabOperacoes);
    }

    private void configurarRecyclerView() {
        adapter = new OperacoesAdapter();
        rvOperacoes.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvOperacoes.setAdapter(adapter);
    }

    /**
     * Implementa a lógica de filtragem via ChipGroup.
     */
    private void configurarChipGroupFiltros() {
        if (chipGroupFiltros == null) return;

        if (chipTodos != null) {
            chipTodos.setChecked(true);
        }

        chipGroupFiltros.setOnCheckedStateChangeListener((group, checkedIds) -> {
            if (checkedIds == null || checkedIds.isEmpty()) return;

            int checkedId = checkedIds.get(0);

            if (checkedId == R.id.chipCinema) {
                // Filtra apenas produções para os Cinemas
                viewModel.aplicarFiltro(OperacoesViewModel.FiltroOperacao.CINEMA);
            } else if (checkedId == R.id.chipDisneyPlus) {
                // Filtra apenas produções para o Disney+
                viewModel.aplicarFiltro(OperacoesViewModel.FiltroOperacao.DISNEY_PLUS);
            } else {
                // Exibe todas as operações futuras
                viewModel.aplicarFiltro(OperacoesViewModel.FiltroOperacao.TODOS);
            }
        });
    }

    private void configurarTabs() {
        if (tabOperacoes == null) return;

        tabOperacoes.addOnTabSelectedListener(new TabLayout.OnTabSelectedListener() {
            @Override
            public void onTabSelected(TabLayout.Tab tab) {
                if (tab == null) return;
                if (tab.getPosition() == 0) {
                    if (layoutCalendario != null) layoutCalendario.setVisibility(View.VISIBLE);
                    if (layoutTermo != null) layoutTermo.setVisibility(View.GONE);
                } else if (tab.getPosition() == 1) {
                    if (layoutCalendario != null) layoutCalendario.setVisibility(View.GONE);
                    if (layoutTermo != null) layoutTermo.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onTabUnselected(TabLayout.Tab tab) {}

            @Override
            public void onTabReselected(TabLayout.Tab tab) {}
        });
    }
}
