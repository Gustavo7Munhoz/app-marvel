package com.example.marvel.ui.quiz

import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.activity.OnBackPressedCallback
import androidx.fragment.app.Fragment
import com.example.marvel.R
import com.example.marvel.databinding.FragmentQuizBinding
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class QuizFragment : Fragment() {

    private var _binding: FragmentQuizBinding? = null
    private val binding get() = _binding!!

    private var currentLevel: QuizLevel = QuizLevel.FACIL
    private var questions: List<QuizQuestion> = emptyList()
    private var currentIndex = 0
    private var score = 0
    private var hasAnswered = false

    private val backPressedCallback = object : OnBackPressedCallback(true) {
        override fun handleOnBackPressed() {
            if (_binding != null && binding.quizContainer.visibility == View.VISIBLE) {
                showExitConfirmationDialog()
            } else {
                isEnabled = false
                requireActivity().onBackPressedDispatcher.onBackPressed()
                isEnabled = true
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enterTransition = com.google.android.material.transition.MaterialFadeThrough()
        exitTransition = com.google.android.material.transition.MaterialFadeThrough()
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentQuizBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        requireActivity().onBackPressedDispatcher.addCallback(viewLifecycleOwner, backPressedCallback)

        setupNavigationAndHeader()
        setupLevelSelection()
        setupGameActions()
    }

    private fun setupNavigationAndHeader() {
        binding.btnQuizBack.setOnClickListener {
            showExitConfirmationDialog()
        }
    }

    private fun showExitConfirmationDialog() {
        MaterialAlertDialogBuilder(requireContext(), com.google.android.material.R.style.ThemeOverlay_MaterialComponents_MaterialAlertDialog)
            .setTitle("Sair do quiz?")
            .setMessage("O progresso será perdido.")
            .setPositiveButton("Sair") { _, _ ->
                abortQuiz()
            }
            .setNegativeButton("Continuar", null)
            .show()
    }

    private fun abortQuiz() {
        binding.quizContainer.visibility = View.GONE
        binding.resultContainer.visibility = View.GONE
        binding.levelSelectContainer.visibility = View.VISIBLE

        binding.btnQuizBack.visibility = View.GONE
        binding.ivShieldLogo.visibility = View.VISIBLE
        setBottomNavVisibility(true)
    }

    private fun setBottomNavVisibility(visible: Boolean) {
        val bottomNav = activity?.findViewById<View>(R.id.bottom_navigation)
        bottomNav?.visibility = if (visible) View.VISIBLE else View.GONE
    }

    private fun setupLevelSelection() {
        binding.btnLevelFacil.setOnClickListener { startQuiz(QuizLevel.FACIL) }
        binding.btnLevelMedio.setOnClickListener { startQuiz(QuizLevel.MEDIO) }
        binding.btnLevelDificil.setOnClickListener { startQuiz(QuizLevel.DIFICIL) }
    }

    private fun startQuiz(level: QuizLevel) {
        currentLevel = level
        questions = QuizRepository.getQuestionsForLevel(level)
        currentIndex = 0
        score = 0
        hasAnswered = false

        binding.levelSelectContainer.visibility = View.GONE
        binding.resultContainer.visibility = View.GONE
        binding.quizContainer.visibility = View.VISIBLE

        // Controle de header e navegação
        binding.btnQuizBack.visibility = View.VISIBLE
        binding.ivShieldLogo.visibility = View.GONE
        setBottomNavVisibility(false)

        binding.quizProgressBar.max = questions.size
        loadQuestion()
    }

    private fun loadQuestion() {
        if (currentIndex !in questions.indices) return
        hasAnswered = false
        val q = questions[currentIndex]

        val levelColor = Color.parseColor(currentLevel.colorHex)

        // Linha de progresso e chip com contorno na cor do nível
        binding.tvQuestionProgress.text = "FASE ${currentIndex + 1} / ${questions.size}"
        binding.quizProgressBar.progress = currentIndex + 1
        binding.quizProgressBar.progressTintList = ColorStateList.valueOf(levelColor)

        binding.tvCurrentLevelBadge.text = currentLevel.badge
        binding.tvCurrentLevelBadge.setTextColor(levelColor)
        val outlineDrawable = GradientDrawable().apply {
            shape = GradientDrawable.RECTANGLE
            cornerRadius = 32f
            setColor(Color.TRANSPARENT)
            setStroke(dpToPx(1.2f), levelColor)
        }
        binding.tvCurrentLevelBadge.background = outlineDrawable

        // Card da pergunta e controles
        binding.tvQuestionText.text = q.question
        binding.cardExplanation.visibility = View.GONE
        binding.btnNextQuestion.visibility = View.GONE
        binding.btnNextQuestion.backgroundTintList = ColorStateList.valueOf(levelColor)
        binding.tvLiveScore.text = "ACERTOS: $score"

        val optionCards = listOf(binding.cardOpt0, binding.cardOpt1, binding.cardOpt2, binding.cardOpt3)
        val optionTexts = listOf(binding.tvOptText0, binding.tvOptText1, binding.tvOptText2, binding.tvOptText3)
        val optionBadges = listOf(binding.badgeLetter0, binding.badgeLetter1, binding.badgeLetter2, binding.badgeLetter3)
        val optionIcons = listOf(binding.ivStatusOpt0, binding.ivStatusOpt1, binding.ivStatusOpt2, binding.ivStatusOpt3)

        optionCards.forEachIndexed { i, card ->
            card.isEnabled = true
            card.alpha = 1.0f
            card.setCardBackgroundColor(Color.parseColor("#1C1C1C"))
            card.strokeColor = Color.parseColor("#333333")
            card.strokeWidth = dpToPx(1f)
            optionBadges[i].setBackgroundResource(R.drawable.bg_quiz_letter_circle)
            optionIcons[i].visibility = View.GONE
            optionTexts[i].text = q.options[i]

            card.setOnClickListener {
                if (!hasAnswered) {
                    evaluateAnswer(i)
                }
            }
        }
    }

    private fun evaluateAnswer(selectedIndex: Int) {
        hasAnswered = true
        val q = questions[currentIndex]
        val optionCards = listOf(binding.cardOpt0, binding.cardOpt1, binding.cardOpt2, binding.cardOpt3)
        val optionIcons = listOf(binding.ivStatusOpt0, binding.ivStatusOpt1, binding.ivStatusOpt2, binding.ivStatusOpt3)

        optionCards.forEach { it.isEnabled = false }

        val isCorrect = (selectedIndex == q.correctIndex)
        if (isCorrect) {
            score++
        }
        binding.tvLiveScore.text = "ACERTOS: $score"

        val greenColor = Color.parseColor("#2E7D32")
        val redColor = Color.parseColor("#C62828")

        optionCards.forEachIndexed { i, card ->
            when (i) {
                q.correctIndex -> {
                    // Opção correta sempre destacada em verde com ícone de check
                    card.alpha = 1.0f
                    card.strokeColor = greenColor
                    card.strokeWidth = dpToPx(1.5f)
                    card.setCardBackgroundColor(Color.parseColor("#172619"))
                    optionIcons[i].visibility = View.VISIBLE
                    optionIcons[i].setImageResource(R.drawable.ic_quiz_check)
                    optionIcons[i].imageTintList = ColorStateList.valueOf(greenColor)
                }
                selectedIndex -> {
                    // Se o usuário selecionou uma opção errada, destaca em vermelho com ícone X
                    card.alpha = 1.0f
                    card.strokeColor = redColor
                    card.strokeWidth = dpToPx(1.5f)
                    card.setCardBackgroundColor(Color.parseColor("#291517"))
                    optionIcons[i].visibility = View.VISIBLE
                    optionIcons[i].setImageResource(R.drawable.ic_quiz_close)
                    optionIcons[i].imageTintList = ColorStateList.valueOf(redColor)
                }
                else -> {
                    // As demais alternativas são desabilitadas com alpha 0.5
                    card.alpha = 0.5f
                    optionIcons[i].visibility = View.GONE
                }
            }
        }

        binding.tvExplanation.text = q.explanation
        binding.cardExplanation.visibility = View.VISIBLE
        binding.btnNextQuestion.visibility = View.VISIBLE
    }

    private fun setupGameActions() {
        binding.btnNextQuestion.setOnClickListener {
            currentIndex++
            if (currentIndex < questions.size) {
                loadQuestion()
            } else {
                showResults()
            }
        }

        binding.btnRestartQuiz.setOnClickListener {
            binding.resultContainer.visibility = View.GONE
            binding.quizContainer.visibility = View.GONE
            binding.levelSelectContainer.visibility = View.VISIBLE

            binding.btnQuizBack.visibility = View.GONE
            binding.ivShieldLogo.visibility = View.VISIBLE
            setBottomNavVisibility(true)
        }
    }

    private fun showResults() {
        binding.quizContainer.visibility = View.GONE
        binding.resultContainer.visibility = View.VISIBLE

        binding.btnQuizBack.visibility = View.GONE
        binding.ivShieldLogo.visibility = View.VISIBLE
        setBottomNavVisibility(true)

        val total = questions.size
        val percent = (score.toFloat() / total * 100).toInt()

        binding.tvFinalScore.text = "$score / $total"
        binding.tvAccuracyPercentage.text = "$percent% DE PRECISÃO OPERACIONAL"

        val rank = when {
            score == 5 && currentLevel == QuizLevel.DIFICIL -> "DIRETOR SUPREMO // NÍVEL 10"
            score == 5 -> "ESPECIALISTA S.H.I.E.L.D. // NÍVEL 8"
            score >= 4 -> "AGENTE DE CAMPO SÊNIOR"
            score >= 3 -> "AGENTE OPERATIVO NÍVEL 5"
            score >= 2 -> "RECRUTA DA ACADEMIA"
            else -> "CIVIL SOB OBSERVAÇÃO"
        }
        binding.tvRankTitle.text = rank
    }

    private fun dpToPx(dp: Float): Int {
        val density = resources.displayMetrics.density
        return (dp * density).toInt()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Garante a restauração da barra de navegação caso o usuário navegue para fora
        setBottomNavVisibility(true)
        _binding = null
    }
}
