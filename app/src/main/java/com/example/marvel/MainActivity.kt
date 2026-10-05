package com.example.marvel

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.marvel.databinding.ActivityMainBinding
import dagger.hilt.android.AndroidEntryPoint
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Setup Bottom Navigation with Navigation Component
        val navHostFragment = supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController
        binding.bottomNavigation.setupWithNavController(navController)

        // Fade in suave da BottomNavigationView na entrada da tela
        binding.bottomNavigation.alpha = 0f
        binding.bottomNavigation.animate()
            .alpha(1f)
            .setDuration(400)
            .setStartDelay(100)
            .start()
    }
}
