package com.example.marvel

import android.animation.Animator
import android.animation.AnimatorListenerAdapter
import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.app.ActivityOptions
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.view.HapticFeedbackConstants
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.AccelerateInterpolator
import android.view.animation.LinearInterpolator
import androidx.appcompat.app.AppCompatActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.example.marvel.databinding.ActivitySplashBinding

class SplashActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySplashBinding

    private enum class SplashState {
        ENTRANCE,
        SCANNING,
        TRANSITIONING,
        FINISHED
    }

    private var currentState = SplashState.ENTRANCE
    private var pulseAnimator: ObjectAnimator? = null
    private val activeAnimators = mutableListOf<Animator>()
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        binding = ActivitySplashBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Modo imersivo em tela cheia
        @Suppress("DEPRECATION")
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_FULLSCREEN or
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        )

        startEntranceAnimation()

        // Tela inteira clicável
        binding.root.setOnClickListener {
            handleScreenTouch()
        }
    }

    override fun onPause() {
        super.onPause()
        stopAllAnimations()
    }

    override fun onDestroy() {
        super.onDestroy()
        stopAllAnimations()
        handler.removeCallbacksAndMessages(null)
    }

    private fun handleScreenTouch() {
        when (currentState) {
            SplashState.ENTRANCE -> {
                // Checagem de acessibilidade: animações desligadas no sistema
                if (isAnimationScaleZero()) {
                    goToMainImmediate()
                    return
                }
                startAccessSequence()
            }
            SplashState.SCANNING -> {
                // Toque durante a sequência: pula direto para o Passo D (Zoom e transição)
                skipToPassoD()
            }
            SplashState.TRANSITIONING, SplashState.FINISHED -> {
                // Transição já em andamento, ignorar
            }
        }
    }

    private fun isAnimationScaleZero(): Boolean {
        return try {
            val scale = Settings.Global.getFloat(
                contentResolver,
                Settings.Global.ANIMATOR_DURATION_SCALE,
                1.0f
            )
            scale == 0f
        } catch (_: Exception) {
            false
        }
    }

    /**
     * PARTE 2: Animação de entrada da Splash (até 1,2s)
     * - Logo: fade in + escala de 0.9 para 1.0 (400ms)
     * - Título: fade in com 200ms de atraso (400ms)
     * - "TOQUE PARA ENTRAR": surge aos 600ms e inicia o pulso
     */
    private fun startEntranceAnimation() {
        val interpolator = AccelerateDecelerateInterpolator()

        // 1. Logo: alpha 0 -> 1, scale 0.9 -> 1.0 (400ms)
        val logoFade = ObjectAnimator.ofFloat(binding.ivSplashLogo, View.ALPHA, 0f, 1f)
        val logoScaleX = ObjectAnimator.ofFloat(binding.ivSplashLogo, View.SCALE_X, 0.9f, 1f)
        val logoScaleY = ObjectAnimator.ofFloat(binding.ivSplashLogo, View.SCALE_Y, 0.9f, 1f)

        val logoSet = AnimatorSet().apply {
            playTogether(logoFade, logoScaleX, logoScaleY)
            duration = 400
            this.interpolator = interpolator
        }

        // 2. Título "S.H.I.E.L.D.": fade in aos 200ms (duração 400ms)
        val titleFade = ObjectAnimator.ofFloat(binding.tvSplashTitle, View.ALPHA, 0f, 1f).apply {
            duration = 400
            startDelay = 200
            this.interpolator = interpolator
        }

        // 3. Botão "TOQUE PARA ENTRAR": fade in aos 600ms (duração 400ms)
        val buttonFade = ObjectAnimator.ofFloat(binding.tvEnterButton, View.ALPHA, 0f, 1f).apply {
            duration = 400
            startDelay = 600
            this.interpolator = interpolator
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    if (currentState == SplashState.ENTRANCE) {
                        startEnterPulse()
                    }
                }
            })
        }

        trackAnimator(logoSet)
        trackAnimator(titleFade)
        trackAnimator(buttonFade)

        logoSet.start()
        titleFade.start()
        buttonFade.start()
    }

    /**
     * Pulso contínuo de alpha entre 0.5 e 1.0 (1,5s, repeatMode reverse)
     */
    private fun startEnterPulse() {
        pulseAnimator?.cancel()
        pulseAnimator = ObjectAnimator.ofFloat(binding.tvEnterButton, View.ALPHA, 1.0f, 0.5f).apply {
            duration = 1500
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
            interpolator = AccelerateDecelerateInterpolator()
        }
        pulseAnimator?.start()
    }

    /**
     * PARTE 3: SEQUÊNCIA DE ACESSO
     */
    private fun startAccessSequence() {
        currentState = SplashState.SCANNING
        pulseAnimator?.cancel()
        pulseAnimator = null

        // Passo A (400ms): fade out de título e botão, logo desliza suavemente ao centro e escala 1.15
        val rootHeight = binding.splashRoot.height.toFloat()
        val logoHeight = binding.logoContainer.height.toFloat()
        val targetCenterY = (rootHeight - logoHeight) / 2f
        val deltaY = targetCenterY - binding.logoContainer.top.toFloat()

        val titleFadeOut = ObjectAnimator.ofFloat(binding.tvSplashTitle, View.ALPHA, binding.tvSplashTitle.alpha, 0f)
        val buttonFadeOut = ObjectAnimator.ofFloat(binding.tvEnterButton, View.ALPHA, binding.tvEnterButton.alpha, 0f)
        val logoSlideY = ObjectAnimator.ofFloat(binding.logoContainer, View.TRANSLATION_Y, 0f, deltaY)
        val logoScaleX = ObjectAnimator.ofFloat(binding.logoContainer, View.SCALE_X, 1f, 1.15f)
        val logoScaleY = ObjectAnimator.ofFloat(binding.logoContainer, View.SCALE_Y, 1f, 1.15f)

        val passoASet = AnimatorSet().apply {
            playTogether(titleFadeOut, buttonFadeOut, logoSlideY, logoScaleX, logoScaleY)
            duration = 400
            interpolator = AccelerateDecelerateInterpolator()
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    if (currentState == SplashState.SCANNING) {
                        startPassoBC()
                    }
                }
            })
        }

        trackAnimator(passoASet)
        passoASet.start()
    }

    /**
     * Passos B e C executados em paralelo
     * - Passo B (900ms): Scanner horizontal fino percorre a logo + brilho dourado
     * - Passo C (1000ms): Efeito de digitação abaixo da logo + vibração curta
     */
    private fun startPassoBC() {
        // Exibir e preparar a linha de scanner
        binding.viewScannerLine.visibility = View.VISIBLE
        binding.viewScannerLine.translationY = 0f

        val scannerAnimator = ObjectAnimator.ofFloat(
            binding.viewScannerLine,
            View.TRANSLATION_Y,
            0f,
            binding.logoContainer.height.toFloat()
        ).apply {
            duration = 900
            interpolator = AccelerateDecelerateInterpolator()
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    binding.viewScannerLine.visibility = View.GONE
                }
            })
        }

        // Breve brilho dourado / flash na logo durante a varredura
        val logoGlow = ObjectAnimator.ofFloat(binding.ivSplashLogo, View.ALPHA, 0.8f, 1.0f).apply {
            duration = 450
            repeatMode = ValueAnimator.REVERSE
            repeatCount = 1
        }

        // Passo C: Digitação no TextView
        binding.tvAccessStatus.visibility = View.VISIBLE
        binding.tvAccessStatus.alpha = 1f
        binding.tvAccessStatus.text = ""

        val text1 = "VERIFICANDO CREDENCIAIS..."
        val text2 = "ACESSO CONCEDIDO  ✓"

        val typewriter = ValueAnimator.ofInt(0, text1.length).apply {
            duration = 750
            interpolator = LinearInterpolator()
            addUpdateListener { va ->
                val len = va.animatedValue as Int
                binding.tvAccessStatus.text = text1.substring(0, len)
            }
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    if (currentState == SplashState.SCANNING) {
                        binding.tvAccessStatus.text = text2
                        triggerHapticFeedback()

                        // Atraso breve antes do Passo D (zoom e transição)
                        handler.postDelayed({
                            if (currentState == SplashState.SCANNING) {
                                executePassoD()
                            }
                        }, 250)
                    }
                }
            })
        }

        val passoBCSet = AnimatorSet().apply {
            playTogether(scannerAnimator, logoGlow, typewriter)
        }

        trackAnimator(passoBCSet)
        passoBCSet.start()
    }

    /**
     * Passo D (500ms): Zoom da logo de 1.15 para 12x, fade out, inicia MainActivity
     */
    private fun executePassoD() {
        currentState = SplashState.TRANSITIONING
        stopAllAnimations()

        binding.viewScannerLine.visibility = View.GONE

        val zoomX = ObjectAnimator.ofFloat(binding.logoContainer, View.SCALE_X, binding.logoContainer.scaleX, 12f)
        val zoomY = ObjectAnimator.ofFloat(binding.logoContainer, View.SCALE_Y, binding.logoContainer.scaleY, 12f)
        val fadeLogo = ObjectAnimator.ofFloat(binding.logoContainer, View.ALPHA, binding.logoContainer.alpha, 0f)
        val fadeStatus = ObjectAnimator.ofFloat(binding.tvAccessStatus, View.ALPHA, binding.tvAccessStatus.alpha, 0f)

        val passoDSet = AnimatorSet().apply {
            playTogether(zoomX, zoomY, fadeLogo, fadeStatus)
            duration = 500
            interpolator = AccelerateInterpolator(1.8f)
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    currentState = SplashState.FINISHED
                }
            })
        }

        trackAnimator(passoDSet)
        passoDSet.start()

        // Lança a MainActivity simultaneamente com animação customizada
        val intent = Intent(this, MainActivity::class.java)
        val options = ActivityOptions.makeCustomAnimation(this, android.R.anim.fade_in, 0)
        startActivity(intent, options.toBundle())
        finish()
    }

    /**
     * Caso o usuário toque na tela durante a sequência, pula direto para o Passo D
     */
    private fun skipToPassoD() {
        handler.removeCallbacksAndMessages(null)
        executePassoD()
    }

    private fun goToMainImmediate() {
        currentState = SplashState.FINISHED
        stopAllAnimations()
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }

    private fun triggerHapticFeedback() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                binding.root.performHapticFeedback(HapticFeedbackConstants.CONFIRM)
            } else {
                binding.root.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
            }
        } catch (_: Exception) {}
    }

    private fun trackAnimator(animator: Animator) {
        activeAnimators.add(animator)
        animator.addListener(object : AnimatorListenerAdapter() {
            override fun onAnimationEnd(animation: Animator) {
                activeAnimators.remove(animation)
            }
        })
    }

    private fun stopAllAnimations() {
        pulseAnimator?.cancel()
        pulseAnimator = null

        val toCancel = ArrayList(activeAnimators)
        activeAnimators.clear()
        for (anim in toCancel) {
            anim.cancel()
        }
    }
}
