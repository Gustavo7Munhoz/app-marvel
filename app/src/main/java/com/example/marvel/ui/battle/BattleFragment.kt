package com.example.marvel.ui.battle

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Typeface
import android.graphics.drawable.BitmapDrawable
import android.graphics.drawable.Drawable
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.example.marvel.databinding.FragmentBattleBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import kotlin.math.abs

@AndroidEntryPoint
class BattleFragment : Fragment() {

    private var _binding: FragmentBattleBinding? = null
    private val binding get() = _binding!!

    private val viewModel: BattleViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enterTransition = com.google.android.material.transition.MaterialFadeThrough()
        exitTransition = com.google.android.material.transition.MaterialFadeThrough()
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentBattleBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupInputValidation()
        setupQuickChips()

        binding.btnCompare.setOnClickListener {
            val f1 = binding.etFighter1.text.toString().trim()
            val f2 = binding.etFighter2.text.toString().trim()

            if (f1.isBlank() || f2.isBlank()) {
                Toast.makeText(context, "Digite o nome dos 2 combatentes para comparar!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            viewModel.simulateBattle(f1, f2)
        }

        observeViewModel()
    }

    private fun setupInputValidation() {
        val watcher = object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {
                updateCompareButtonState()
            }
            override fun afterTextChanged(s: Editable?) {}
        }

        binding.etFighter1.addTextChangedListener(watcher)
        binding.etFighter2.addTextChangedListener(watcher)
        updateCompareButtonState()
    }

    private fun updateCompareButtonState() {
        val canCompare = binding.etFighter1.text?.isNotBlank() == true &&
                binding.etFighter2.text?.isNotBlank() == true
        binding.btnCompare.isEnabled = canCompare
        binding.btnCompare.alpha = if (canCompare) 1.0f else 0.4f
    }

    private fun setupQuickChips() {
        binding.chipDuelo1.setOnClickListener {
            binding.etFighter1.setText("Iron Man")
            binding.etFighter2.setText("Captain America")
            binding.btnCompare.performClick()
        }
        binding.chipDuelo2.setOnClickListener {
            binding.etFighter1.setText("Thor")
            binding.etFighter2.setText("Hulk")
            binding.btnCompare.performClick()
        }
        binding.chipDuelo3.setOnClickListener {
            binding.etFighter1.setText("Spider-Man")
            binding.etFighter2.setText("Venom")
            binding.btnCompare.performClick()
        }
    }

    private fun observeViewModel() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    when (state) {
                        is BattleUiState.Idle -> {
                            binding.progressBar.visibility = View.GONE
                            binding.tvMessage.visibility = View.GONE
                            binding.cardResults.visibility = View.GONE
                        }
                        is BattleUiState.Loading -> {
                            binding.progressBar.visibility = View.VISIBLE
                            binding.tvMessage.visibility = View.GONE
                            binding.cardResults.visibility = View.GONE
                        }
                        is BattleUiState.Success -> {
                            binding.progressBar.visibility = View.GONE
                            binding.tvMessage.visibility = View.GONE
                            binding.cardResults.visibility = View.VISIBLE

                            val p1 = state.fighter1
                            val p2 = state.fighter2

                            binding.tvName1.text = p1.name.uppercase()
                            binding.tvName2.text = p2.name.uppercase()

                            // Placeholder escuro #2A2A2A com iniciais do personagem (nunca caixa preta vazia)
                            val placeholder1 = createInitialsDrawable(requireContext(), p1.name, 300, 400)
                            val placeholder2 = createInitialsDrawable(requireContext(), p2.name, 300, 400)

                            Glide.with(this@BattleFragment)
                                .load(state.imageUrl1)
                                .placeholder(placeholder1)
                                .error(placeholder1)
                                .fallback(placeholder1)
                                .diskCacheStrategy(DiskCacheStrategy.ALL)
                                .into(binding.ivFighter1)

                            Glide.with(this@BattleFragment)
                                .load(state.imageUrl2)
                                .placeholder(placeholder2)
                                .error(placeholder2)
                                .fallback(placeholder2)
                                .diskCacheStrategy(DiskCacheStrategy.ALL)
                                .into(binding.ivFighter2)

                            // Estatísticas comparativas
                            val int1 = p1.powerstats.intelligence.toIntOrNull() ?: 0
                            val int2 = p2.powerstats.intelligence.toIntOrNull() ?: 0
                            updateAttributeRow(int1, int2, binding.tvInt1, binding.tvInt2, binding.pbInt1, binding.pbInt2)

                            val str1 = p1.powerstats.strength.toIntOrNull() ?: 0
                            val str2 = p2.powerstats.strength.toIntOrNull() ?: 0
                            updateAttributeRow(str1, str2, binding.tvStr1, binding.tvStr2, binding.pbStr1, binding.pbStr2)

                            val spd1 = p1.powerstats.speed.toIntOrNull() ?: 0
                            val spd2 = p2.powerstats.speed.toIntOrNull() ?: 0
                            updateAttributeRow(spd1, spd2, binding.tvSpd1, binding.tvSpd2, binding.pbSpd1, binding.pbSpd2)

                            val dur1 = p1.powerstats.durability.toIntOrNull() ?: 0
                            val dur2 = p2.powerstats.durability.toIntOrNull() ?: 0
                            updateAttributeRow(dur1, dur2, binding.tvDur1, binding.tvDur2, binding.pbDur1, binding.pbDur2)

                            val pow1 = p1.powerstats.power.toIntOrNull() ?: 0
                            val pow2 = p2.powerstats.power.toIntOrNull() ?: 0
                            updateAttributeRow(pow1, pow2, binding.tvPow1, binding.tvPow2, binding.pbPow1, binding.pbPow2)

                            val com1 = p1.powerstats.combat.toIntOrNull() ?: 0
                            val com2 = p2.powerstats.combat.toIntOrNull() ?: 0
                            updateAttributeRow(com1, com2, binding.tvCom1, binding.tvCom2, binding.pbCom1, binding.pbCom2)

                            val total1 = int1 + str1 + spd1 + dur1 + pow1 + com1
                            val total2 = int2 + str2 + spd2 + dur2 + pow2 + com2
                            val diff = abs(total1 - total2)

                            val colorP1 = Color.parseColor("#29B6F6")
                            val colorP2 = Color.parseColor("#E53935")
                            val colorNeutral = Color.parseColor("#EAEAEA")

                            if (total1 > total2) {
                                binding.tvPowerDiffTotal.text = "VANTAGEM: +$diff PONTOS PARA ${p1.name.uppercase()}"
                                binding.tvPowerDiffTotal.setTextColor(colorP1)
                                binding.tvWinner.text = "VITÓRIA PROVÁVEL DE ${p1.name.uppercase()}"
                                binding.tvWinner.setTextColor(colorP1)
                            } else if (total2 > total1) {
                                binding.tvPowerDiffTotal.text = "VANTAGEM: +$diff PONTOS PARA ${p2.name.uppercase()}"
                                binding.tvPowerDiffTotal.setTextColor(colorP2)
                                binding.tvWinner.text = "VITÓRIA PROVÁVEL DE ${p2.name.uppercase()}"
                                binding.tvWinner.setTextColor(colorP2)
                            } else {
                                binding.tvPowerDiffTotal.text = "EMPATE TÉCNICO"
                                binding.tvPowerDiffTotal.setTextColor(colorNeutral)
                                binding.tvWinner.text = "CONFRONTO IMPREVISÍVEL // EMPATE"
                                binding.tvWinner.setTextColor(colorNeutral)
                            }

                            // Rola suavemente até o card de resultado para não ficar escondido
                            binding.rootScrollView.post {
                                binding.rootScrollView.smoothScrollTo(0, binding.cardResults.top)
                            }
                        }
                        is BattleUiState.Error -> {
                            binding.progressBar.visibility = View.GONE
                            binding.cardResults.visibility = View.GONE
                            binding.tvMessage.visibility = View.VISIBLE
                            binding.tvMessage.text = state.message
                        }
                    }
                }
            }
        }
    }

    private fun updateAttributeRow(
        val1: Int, val2: Int,
        tv1: TextView, tv2: TextView,
        pb1: ProgressBar, pb2: ProgressBar
    ) {
        tv1.text = val1.toString()
        tv2.text = val2.toString()
        pb1.progress = val1.coerceIn(0, 100)
        pb2.progress = val2.coerceIn(0, 100)

        val winnerColor = Color.parseColor("#EAEAEA")
        val loserColor = Color.parseColor("#9A9A9A")

        when {
            val1 > val2 -> {
                tv1.setTextColor(winnerColor)
                tv1.typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD)
                tv2.setTextColor(loserColor)
                tv2.typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.NORMAL)
            }
            val2 > val1 -> {
                tv1.setTextColor(loserColor)
                tv1.typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.NORMAL)
                tv2.setTextColor(winnerColor)
                tv2.typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD)
            }
            else -> {
                tv1.setTextColor(winnerColor)
                tv1.typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD)
                tv2.setTextColor(winnerColor)
                tv2.typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD)
            }
        }
    }

    private fun createInitialsDrawable(context: Context, name: String, width: Int, height: Int): Drawable {
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)

        // Fundo escuro #2A2A2A
        val bgPaint = Paint().apply {
            color = Color.parseColor("#2A2A2A")
            isAntiAlias = true
        }
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), bgPaint)

        // Extrai as iniciais do personagem (ex: "Iron Man" -> "IM")
        val words = name.trim().split("\\s+".toRegex()).filter { it.isNotBlank() }
        val initials = when {
            words.size >= 2 -> "${words[0].first().uppercaseChar()}${words[1].first().uppercaseChar()}"
            words.size == 1 && words[0].length >= 2 -> words[0].take(2).uppercase()
            words.size == 1 -> words[0].take(1).uppercase()
            else -> "SH"
        }

        // Texto em negrito #EAEAEA
        val textPaint = Paint().apply {
            color = Color.parseColor("#EAEAEA")
            textSize = height * 0.28f
            isFakeBoldText = true
            isAntiAlias = true
            textAlign = Paint.Align.CENTER
            typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD)
        }

        val xPos = width / 2f
        val yPos = (height / 2f - (textPaint.descent() + textPaint.ascent()) / 2f)
        canvas.drawText(initials, xPos, yPos, textPaint)

        return BitmapDrawable(context.resources, bitmap)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
