package com.example.marvel.ui.quiz

data class QuizQuestion(
    val id: Int,
    val question: String,
    val options: List<String>,
    val correctIndex: Int,
    val explanation: String
)

enum class QuizLevel(val title: String, val badge: String, val colorHex: String) {
    FACIL("RECRUTA", "RECRUTA", "#2E7D32"),
    MEDIO("ESPECIALISTA", "ESPECIALISTA", "#F9A825"),
    DIFICIL("DIRETOR", "DIRETOR", "#C62828")
}

object QuizRepository {

    val facilQuestions = listOf(
        QuizQuestion(
            id = 1,
            question = "Qual é o nome civil do Homem de Ferro?",
            options = listOf("Steve Rogers", "Tony Stark", "Bruce Banner", "Peter Parker"),
            correctIndex = 1,
            explanation = "Tony Stark é o gênio, bilionário, playboy e filantropo criador das armaduras."
        ),
        QuizQuestion(
            id = 2,
            question = "De qual reino mitológico o herói Thor se origina?",
            options = listOf("Asgard", "Midgard", "Jotunheim", "Nidavellir"),
            correctIndex = 0,
            explanation = "Thor é o Príncipe de Asgard, filho de Odin e Deus do Trovão."
        ),
        QuizQuestion(
            id = 3,
            question = "De qual metal quase indestrutível é feito o escudo do Capitão América?",
            options = listOf("Adamantium", "Vibranium", "Uru", "Titanium"),
            correctIndex = 1,
            explanation = "O escudo de Steve Rogers foi forjado por Howard Stark usando Vibranium de Wakanda."
        ),
        QuizQuestion(
            id = 4,
            question = "Qual cientista se transforma no Hulk quando fica furioso?",
            options = listOf("Hank Pym", "Stephen Strange", "Bruce Banner", "Reed Richards"),
            correctIndex = 2,
            explanation = "Dr. Bruce Banner foi exposto à radiação gama durante experimentos militares."
        ),
        QuizQuestion(
            id = 5,
            question = "Qual é o nome do jovem que assume o manto do Homem-Aranha no Queens?",
            options = listOf("Miles Morales", "Peter Parker", "Ned Leeds", "Harry Osborn"),
            correctIndex = 1,
            explanation = "Peter Parker foi picado por uma aranha geneticamente modificada aos 15 anos."
        )
    )

    val medioQuestions = listOf(
        QuizQuestion(
            id = 1,
            question = "Qual Inteligência Artificial ocupou o corpo sintético e virou o herói Visão?",
            options = listOf("K.A.R.E.N.", "J.A.R.V.I.S.", "F.R.I.D.A.Y.", "E.D.I.T.H."),
            correctIndex = 1,
            explanation = "Tony Stark e Bruce Banner integraram J.A.R.V.I.S. ao corpo biológico energizado pela Joia da Mente."
        ),
        QuizQuestion(
            id = 2,
            question = "Em qual planeta desolado estava oculta a Joia da Alma em Vormir?",
            options = listOf("Knowhere", "Vormir", "Sakaar", "Morag"),
            correctIndex = 1,
            explanation = "Vormir era guardado pelo Caveira Vermelha, onde uma alma requeria o sacrifício de outra."
        ),
        QuizQuestion(
            id = 3,
            question = "Quem foi o responsável por arrancar o olho de Thor em Thor: Ragnarok?",
            options = listOf("Loki", "Hela", "Surtur", "Thanos"),
            correctIndex = 1,
            explanation = "Hela, a Deusa da Morte e irmã mais velha de Thor, cortou o olho direito dele durante o duelo."
        ),
        QuizQuestion(
            id = 4,
            question = "Qual substância rara é minerada exclusivamente em Wakanda?",
            options = listOf("Adamantium", "Carbonádio", "Vibranium", "Promethium"),
            correctIndex = 2,
            explanation = "Um meteorito de Vibranium caiu em Wakanda há milhões de anos, transformando sua tecnologia."
        ),
        QuizQuestion(
            id = 5,
            question = "Qual vingador tem a habilidade de encolher e crescer usando as Partículas Pym?",
            options = listOf("Gavião Arqueiro", "Homem-Formiga", "Falcão", "Máquina de Combate"),
            correctIndex = 1,
            explanation = "Scott Lang usa o traje desenvolvido pelo cientista Hank Pym."
        )
    )

    val dificilQuestions = listOf(
        QuizQuestion(
            id = 1,
            question = "Qual é o nome completo do Soldado Invernal nos arquivos da S.H.I.E.L.D.?",
            options = listOf("James Buchanan Barnes", "James Rhodes Barnes", "Steven Grant Barnes", "John Walker Barnes"),
            correctIndex = 0,
            explanation = "O sargento James Buchanan 'Bucky' Barnes era o melhor amigo de infância de Steve Rogers."
        ),
        QuizQuestion(
            id = 2,
            question = "Qual era o nome da nave original dos Guardiões da Galáxia pilotada por Peter Quill?",
            options = listOf("Benatar", "Milano", "Bowie", "Sanctuary II"),
            correctIndex = 1,
            explanation = "A Milano foi batizada em homenagem à atriz Alyssa Milano, paixão de infância de Quill."
        ),
        QuizQuestion(
            id = 3,
            question = "Qual forjador gigante fabricou a Manopla do Infinito e a Stormbreaker?",
            options = listOf("Bor", "Eitri", "Heimdall", "Miek"),
            correctIndex = 1,
            explanation = "Eitri, o Rei dos Anões de Nidavellir, interpretado por Peter Dinklage."
        ),
        QuizQuestion(
            id = 4,
            question = "Em qual revista de quadrinhos de 1962 o Homem-Aranha apareceu pela primeira vez?",
            options = listOf("Action Comics #1", "Tales of Suspense #39", "Amazing Fantasy #15", "Journey into Mystery #83"),
            correctIndex = 2,
            explanation = "Criado por Stan Lee e Steve Ditko, sua estreia foi na clássica Amazing Fantasy #15 de agosto de 1962."
        ),
        QuizQuestion(
            id = 5,
            question = "Qual é a frase exata gravada no martelo Mjolnir para definir quem pode erguê-lo?",
            options = listOf(
                "Aquele que tiver coragem reinará com a força de Asgard",
                "Aquele que empunhar este martelo, se for digno, possuirá o poder de Thor",
                "Somente o rei legítimo de Asgard terá o poder dos trovões",
                "O verdadeiro guerreiro comandará as tempestades celestiais"
            ),
            correctIndex = 1,
            explanation = "O encantamento de Odin diz: 'Whosoever holds this hammer, if he be worthy, shall possess the power of Thor'."
        )
    )

    fun getQuestionsForLevel(level: QuizLevel): List<QuizQuestion> = when (level) {
        QuizLevel.FACIL -> facilQuestions
        QuizLevel.MEDIO -> medioQuestions
        QuizLevel.DIFICIL -> dificilQuestions
    }
}
