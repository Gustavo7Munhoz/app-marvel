package com.example.marvel.adapter;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentActivity;
import androidx.viewpager2.adapter.FragmentStateAdapter;
import com.example.marvel.ui.calendar.CalendarFragment;

/**
 * Adapter do ViewPager2 para conectar o TabLayout com as abas de Operações:
 * Aba 0: CALENDÁRIO DE OPERAÇÕES
 * Aba 1: TERMO OPERATIVO
 */
public class OperacoesPagerAdapter extends FragmentStateAdapter {

    public OperacoesPagerAdapter(@NonNull FragmentActivity fragmentActivity) {
        super(fragmentActivity);
    }

    public OperacoesPagerAdapter(@NonNull Fragment fragment) {
        super(fragment);
    }

    @NonNull
    @Override
    public Fragment createFragment(int position) {
        switch (position) {
            case 1:
                return new CalendarFragment(); // Aba Termo
            case 0:
            default:
                return new CalendarFragment(); // Aba Calendário de Lançamentos
        }
    }

    @Override
    public int getItemCount() {
        return 2;
    }
}
