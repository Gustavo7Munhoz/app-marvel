package com.example.marvel;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Fragment de Simulação X1 (Versus) da S.H.I.E.L.D. em Java puro.
 */
public class X1Fragment extends Fragment {

    private Spinner spCombatente1;
    private Spinner spCombatente2;
    private Button btnComparar;
    private TextView tvResultado;

    // Tabela de Níveis de Poder Tático S.H.I.E.L.D. (0 - 100)
    private final Map<String, Integer> poderMap = new LinkedHashMap<String, Integer>() {{
        put("Thanos (Titã Louco)", 100);
        put("Doutor Destino (Victor von Doom)", 99);
        put("Thor Odinson", 98);
        put("Hulk (Bruce Banner)", 97);
        put("Doutor Estranho", 95);
        put("Feiticeira Escarlate (Wanda)", 99);
        put("Capitã Marvel (Carol Danvers)", 96);
        put("Homem de Ferro (Mark 85)", 89);
        put("Sentinela (Bob Reynolds)", 99);
        put("Capitão América (Sam Wilson)", 82);
        put("Homem-Aranha (Peter Parker)", 86);
        put("Pantera Negra (Shuri)", 84);
        put("Demolidor (Matt Murdock)", 75);
    }};

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_x1, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        spCombatente1 = view.findViewById(R.id.sp_combatente_1);
        spCombatente2 = view.findViewById(R.id.sp_combatente_2);
        btnComparar = view.findViewById(R.id.btn_comparar_poder);
        tvResultado = view.findViewById(R.id.tv_resultado_comparacao);

        String[] combatentes = poderMap.keySet().toArray(new String[0]);

        ArrayAdapter<String> adapter = new ArrayAdapter<>(
                requireContext(),
                android.R.layout.simple_spinner_dropdown_item,
                combatentes
        );

        spCombatente1.setAdapter(adapter);
        spCombatente2.setAdapter(adapter);

        // Seleciona o 1º e 2º combatentes por padrão
        spCombatente1.setSelection(0); // Thanos
        spCombatente2.setSelection(1); // Doutor Destino

        btnComparar.setOnClickListener(v -> executarComparativo());
    }

    private void executarComparativo() {
        if (spCombatente1.getSelectedItem() == null || spCombatente2.getSelectedItem() == null) {
            return;
        }

        String c1 = spCombatente1.getSelectedItem().toString();
        String c2 = spCombatente2.getSelectedItem().toString();

        Integer p1Obj = poderMap.get(c1);
        Integer p2Obj = poderMap.get(c2);

        int p1 = (p1Obj != null) ? p1Obj : 50;
        int p2 = (p2Obj != null) ? p2Obj : 50;
        int diff = Math.abs(p1 - p2);

        String vencedor;
        if (p1 > p2) {
            vencedor = "VANTAGEM: " + c1.toUpperCase();
        } else if (p2 > p1) {
            vencedor = "VANTAGEM: " + c2.toUpperCase();
        } else {
            vencedor = "EMPATE TÁTICO RIGOROSO (EQUILÍBRIO DE FORÇAS)";
        }

        String relatorio = "═════ S.H.I.E.L.D. RELATÓRIO DE COMBATE ═════\n\n" +
                "• [ALFA] " + c1 + " ➔ NÍVEL DE PODER: " + p1 + "/100\n" +
                "• [BETA] " + c2 + " ➔ NÍVEL DE PODER: " + p2 + "/100\n\n" +
                "• DIFERENCIAL TÁTICO: Δ " + diff + " PONTOS\n" +
                "• " + vencedor + "\n\n" +
                "STATUS DA SIMULAÇÃO: 100% PROCESSADA";

        tvResultado.setText(relatorio);
        tvResultado.setVisibility(View.VISIBLE);
    }
}
