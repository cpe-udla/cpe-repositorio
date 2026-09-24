// Terminal dialéctica — cliente.
//
// Se incrusta en cada página con:
//   <link rel="stylesheet" href="terminal/terminal.css">
//   <script src="terminal/terminal.js" data-servidor="https://<worker>.workers.dev"
//           data-reiniciar="assets/site.js" defer></script>
//
// Dos modos:
//   intervenir  en páginas con zona dialéctica (<!-- ZONA-DIALECTICA:INICIO/FIN -->):
//               la persona transforma la página y, si quiere, publica el cambio.
//   preguntar   en todas las páginas: un modelo lector explica el contenido, un
//               paper o un vídeo. Junto a cada publicación y vídeo aparece un botón.
(function () {
  'use strict';

  const guion = document.currentScript;
  const SERVIDOR = ((guion && guion.dataset.servidor) || '').replace(/\/+$/, '');
  // Raíz del sitio: la carpeta que contiene terminal/terminal.js.
  const RAIZ = new URL('..', guion ? guion.src : location.href);
  const REINICIAR = ((guion && guion.dataset.reiniciar) || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  const CLAVE_FIRMA = 'terminal-dialectica:firma';

  // ── Idiomas ─────────────────────────────────────────────────
  // El idioma se toma de <html lang>. Los comandos en español funcionan siempre;
  // cada idioma añade sus propios nombres de comando.

  const TEXTOS = {
    es: {
      intervenir: '>_ Intervenir', preguntar: '>_ Preguntar',
      abrir: 'Abrir la terminal (tecla º o `)', nombre: 'Terminal dialéctica', cerrar: 'Cerrar terminal',
      tituloEditable: 'Terminal dialéctica — página en proceso', tituloPreguntar: 'Terminal dialéctica — preguntar',
      espacio: 'espacio', phIntervenir: 'describe un cambio, o «?» + pregunta', phPreguntar: 'haz una pregunta sobre esta página',
      btnPub: 'Explicar hallazgos ▸', qPub: (t) => `Explícame los principales hallazgos de «${t}»`,
      btnVideo: '¿De qué trata? ▸', qVideo: (t) => `¿De qué trata el vídeo «${t}»?`,
      ayudaEditable: [
        'Esta página no está terminada: cualquiera puede transformarla,',
        'en su estética y en su organización, sin borrar información.',
        'Describe el cambio, por ejemplo:',
        '  «convierte la portada en una línea de tiempo de la investigación»',
        '  «reorganiza las tarjetas en una sola columna tipográfica»',
        'Verás una vista previa. Luego:',
      ],
      ayudaPreguntar: 'Pregunta lo que quieras sobre esta página, un paper o un vídeo.',
      dAplicar: 'publica la intervención (queda registrada en git)', dDescartar: 'vuelve a la versión anterior',
      dHistoria: 'últimas intervenciones', dVer: 'HTML actual de la página', dFirma: 'firma tus intervenciones (vacío = anónima)',
      argNombre: '<nombre>', argPregunta: '<pregunta>', dPregunta: 'pregunta sobre esta página, un paper o un vídeo',
      dModoPreguntar: 'todo lo que escribas será una pregunta', dModoIntervenir: 'vuelve a transformar la página', dLimpiar: 'limpia la terminal',
      modoFijado: (m) => `Modo ${m}.`, modos: (a, b, c) => `Modos: «${a} ${b}» o «${a} ${c}».`,
      soloPreguntar: 'En esta página solo se puede preguntar.', sinZona: 'Esta página no tiene zona editable.', vacia: '(vacía)',
      firmado: (n) => `Tus intervenciones irán firmadas como «${n}».`, anonima: 'Tus intervenciones serán anónimas.',
      sinHistoria: 'Sin intervenciones todavía.', sinPropuesta: 'No hay ninguna propuesta pendiente.',
      publicando: 'Publicando la intervención…',
      enRevision: 'Propuesta enviada para revisión del CPE. Se publicará cuando sea aceptada:',
      publicada: 'Intervención publicada. Será visible para todas las personas cuando termine el despliegue (≈1 min):',
      descartada: 'Propuesta descartada. La página vuelve a su estado anterior.',
      reescribiendo: 'El modelo está reescribiendo la página (puede tardar hasta un minuto)…',
      vistaPrevia: (a, d) => `Vista previa aplicada. Escribe «${a}» para publicarla o «${d}» para volver atrás.`,
      leyendo: 'Leyendo…', video: 'vídeo', publicacion: 'publicación', textoCompleto: 'texto completo',
      soloTitulo: 'solo título; sin transcripción', soloMetadatos: 'solo metadatos; sin texto completo',
      fuente: (tipo, titulo, base) => `Fuente: ${tipo} «${titulo}» (${base}).`,
      sinServidorAttr: 'La terminal no está conectada a ningún servidor (falta data-servidor).',
      sinServidor: 'La terminal no está conectada a ningún servidor.',
      sinContacto: 'No se pudo contactar al servidor de la terminal.', estadoServidor: (n) => `El servidor respondió ${n}.`,
      fallo: 'Algo falló.',
      bienvenidaEditable: 'Terminal dialéctica. Esta página es un espacio producido colectivamente: puedes transformarla o hacerle preguntas.',
      bienvenidaPreguntar: 'Terminal dialéctica. Pregunta sobre esta página, sus publicaciones o sus vídeos.',
      empezar: (c) => `Escribe «${c}» para empezar.`,
      comandos: { ayuda: 'ayuda', limpiar: 'limpiar', modo: 'modo', ver: 'ver', firma: 'firma', historia: 'historia', aplicar: 'aplicar', descartar: 'descartar' },
      modosNombre: { preguntar: 'preguntar', intervenir: 'intervenir' },
    },
    en: {
      intervenir: '>_ Intervene', preguntar: '>_ Ask',
      abrir: 'Open the terminal (key `)', nombre: 'Dialectical terminal', cerrar: 'Close terminal',
      tituloEditable: 'Dialectical terminal — page in progress', tituloPreguntar: 'Dialectical terminal — ask',
      espacio: 'space', phIntervenir: 'describe a change, or “?” + question', phPreguntar: 'ask a question about this page',
      btnPub: 'Explain findings ▸', qPub: (t) => `Explain the main findings of “${t}”`,
      btnVideo: 'What is it about? ▸', qVideo: (t) => `What is the video “${t}” about?`,
      ayudaEditable: [
        'This page is unfinished: anyone can transform it,',
        'in its aesthetics and its organisation, without deleting information.',
        'Describe the change, for example:',
        '  “turn the home page into a timeline of the research”',
        '  “rearrange the cards into a single typographic column”',
        'You will see a preview. Then:',
      ],
      ayudaPreguntar: 'Ask anything about this page, a paper or a video.',
      dAplicar: 'publish the intervention (recorded in git)', dDescartar: 'return to the previous version',
      dHistoria: 'latest interventions', dVer: 'current HTML of the page', dFirma: 'sign your interventions (empty = anonymous)',
      argNombre: '<name>', argPregunta: '<question>', dPregunta: 'ask about this page, a paper or a video',
      dModoPreguntar: 'everything you type will be a question', dModoIntervenir: 'go back to transforming the page', dLimpiar: 'clear the terminal',
      modoFijado: (m) => `Mode: ${m}.`, modos: (a, b, c) => `Modes: “${a} ${b}” or “${a} ${c}”.`,
      soloPreguntar: 'On this page you can only ask questions.', sinZona: 'This page has no editable zone.', vacia: '(empty)',
      firmado: (n) => `Your interventions will be signed as “${n}”.`, anonima: 'Your interventions will be anonymous.',
      sinHistoria: 'No interventions yet.', sinPropuesta: 'There is no pending proposal.',
      publicando: 'Publishing the intervention…',
      enRevision: 'Proposal sent for review by the CPE. It will be published once accepted:',
      publicada: 'Intervention published. It will be visible to everyone once deployment finishes (≈1 min):',
      descartada: 'Proposal discarded. The page returns to its previous state.',
      reescribiendo: 'The model is rewriting the page (this may take up to a minute)…',
      vistaPrevia: (a, d) => `Preview applied. Type “${a}” to publish it or “${d}” to go back.`,
      leyendo: 'Reading…', video: 'video', publicacion: 'publication', textoCompleto: 'full text',
      soloTitulo: 'title only; no transcript', soloMetadatos: 'metadata only; no full text',
      fuente: (tipo, titulo, base) => `Source: ${tipo} “${titulo}” (${base}).`,
      sinServidorAttr: 'The terminal is not connected to any server (data-servidor is missing).',
      sinServidor: 'The terminal is not connected to any server.',
      sinContacto: 'Could not reach the terminal server.', estadoServidor: (n) => `The server responded ${n}.`,
      fallo: 'Something went wrong.',
      bienvenidaEditable: 'Dialectical terminal. This page is a collectively produced space: you can transform it or ask it questions.',
      bienvenidaPreguntar: 'Dialectical terminal. Ask about this page, its publications or its videos.',
      empezar: (c) => `Type “${c}” to begin.`,
      comandos: { ayuda: 'help', limpiar: 'clear', modo: 'mode', ver: 'view', firma: 'sign', historia: 'history', aplicar: 'apply', descartar: 'discard' },
      modosNombre: { preguntar: 'ask', intervenir: 'intervene' },
    },
    fr: {
      intervenir: '>_ Intervenir', preguntar: '>_ Interroger',
      abrir: 'Ouvrir le terminal (touche `)', nombre: 'Terminal dialectique', cerrar: 'Fermer le terminal',
      tituloEditable: 'Terminal dialectique — page en cours', tituloPreguntar: 'Terminal dialectique — interroger',
      espacio: 'espace', phIntervenir: 'décrivez un changement, ou « ? » + question', phPreguntar: 'posez une question sur cette page',
      btnPub: 'Expliquer les résultats ▸', qPub: (t) => `Explique-moi les principaux résultats de « ${t} »`,
      btnVideo: 'De quoi s’agit-il ? ▸', qVideo: (t) => `De quoi parle la vidéo « ${t} » ?`,
      ayudaEditable: [
        'Cette page n’est pas terminée : chacun peut la transformer,',
        'dans son esthétique et son organisation, sans effacer d’information.',
        'Décrivez le changement, par exemple :',
        '  « transforme l’accueil en une frise chronologique de la recherche »',
        '  « réorganise les cartes en une seule colonne typographique »',
        'Vous verrez un aperçu. Ensuite :',
      ],
      ayudaPreguntar: 'Posez n’importe quelle question sur cette page, un article ou une vidéo.',
      dAplicar: 'publie l’intervention (enregistrée dans git)', dDescartar: 'revient à la version précédente',
      dHistoria: 'dernières interventions', dVer: 'HTML actuel de la page', dFirma: 'signe vos interventions (vide = anonyme)',
      argNombre: '<nom>', argPregunta: '<question>', dPregunta: 'question sur cette page, un article ou une vidéo',
      dModoPreguntar: 'tout ce que vous écrivez sera une question', dModoIntervenir: 'revient à la transformation de la page', dLimpiar: 'efface le terminal',
      modoFijado: (m) => `Mode : ${m}.`, modos: (a, b, c) => `Modes : « ${a} ${b} » ou « ${a} ${c} ».`,
      soloPreguntar: 'Sur cette page, on peut seulement poser des questions.', sinZona: 'Cette page n’a pas de zone modifiable.', vacia: '(vide)',
      firmado: (n) => `Vos interventions seront signées « ${n} ».`, anonima: 'Vos interventions seront anonymes.',
      sinHistoria: 'Aucune intervention pour l’instant.', sinPropuesta: 'Aucune proposition en attente.',
      publicando: 'Publication de l’intervention…',
      enRevision: 'Proposition envoyée pour relecture par le CPE. Elle sera publiée une fois acceptée :',
      publicada: 'Intervention publiée. Elle sera visible par tous à la fin du déploiement (≈1 min) :',
      descartada: 'Proposition abandonnée. La page revient à son état précédent.',
      reescribiendo: 'Le modèle réécrit la page (cela peut prendre jusqu’à une minute)…',
      vistaPrevia: (a, d) => `Aperçu appliqué. Tapez « ${a} » pour le publier ou « ${d} » pour revenir en arrière.`,
      leyendo: 'Lecture…', video: 'vidéo', publicacion: 'publication', textoCompleto: 'texte intégral',
      soloTitulo: 'titre seulement ; sans transcription', soloMetadatos: 'métadonnées seulement ; sans texte intégral',
      fuente: (tipo, titulo, base) => `Source : ${tipo} « ${titulo} » (${base}).`,
      sinServidorAttr: 'Le terminal n’est connecté à aucun serveur (data-servidor manquant).',
      sinServidor: 'Le terminal n’est connecté à aucun serveur.',
      sinContacto: 'Impossible de joindre le serveur du terminal.', estadoServidor: (n) => `Le serveur a répondu ${n}.`,
      fallo: 'Une erreur est survenue.',
      bienvenidaEditable: 'Terminal dialectique. Cette page est un espace produit collectivement : vous pouvez la transformer ou lui poser des questions.',
      bienvenidaPreguntar: 'Terminal dialectique. Posez des questions sur cette page, ses publications ou ses vidéos.',
      empezar: (c) => `Tapez « ${c} » pour commencer.`,
      comandos: { ayuda: 'aide', limpiar: 'effacer', modo: 'mode', ver: 'voir', firma: 'signer', historia: 'historique', aplicar: 'appliquer', descartar: 'abandonner' },
      modosNombre: { preguntar: 'interroger', intervenir: 'intervenir' },
    },
    pt: {
      intervenir: '>_ Intervir', preguntar: '>_ Perguntar',
      abrir: 'Abrir o terminal (tecla `)', nombre: 'Terminal dialético', cerrar: 'Fechar o terminal',
      tituloEditable: 'Terminal dialético — página em processo', tituloPreguntar: 'Terminal dialético — perguntar',
      espacio: 'espaço', phIntervenir: 'descreva uma mudança, ou «?» + pergunta', phPreguntar: 'faça uma pergunta sobre esta página',
      btnPub: 'Explicar resultados ▸', qPub: (t) => `Explique-me os principais resultados de «${t}»`,
      btnVideo: 'Do que trata? ▸', qVideo: (t) => `Do que trata o vídeo «${t}»?`,
      ayudaEditable: [
        'Esta página não está terminada: qualquer pessoa pode transformá-la,',
        'na sua estética e na sua organização, sem apagar informação.',
        'Descreva a mudança, por exemplo:',
        '  «transforme a página inicial numa linha do tempo da pesquisa»',
        '  «reorganize os cartões numa única coluna tipográfica»',
        'Verá uma pré-visualização. Depois:',
      ],
      ayudaPreguntar: 'Pergunte o que quiser sobre esta página, um artigo ou um vídeo.',
      dAplicar: 'publica a intervenção (fica registrada no git)', dDescartar: 'volta à versão anterior',
      dHistoria: 'últimas intervenções', dVer: 'HTML atual da página', dFirma: 'assina as suas intervenções (vazio = anônima)',
      argNombre: '<nome>', argPregunta: '<pergunta>', dPregunta: 'pergunta sobre esta página, um artigo ou um vídeo',
      dModoPreguntar: 'tudo o que escrever será uma pergunta', dModoIntervenir: 'volta a transformar a página', dLimpiar: 'limpa o terminal',
      modoFijado: (m) => `Modo ${m}.`, modos: (a, b, c) => `Modos: «${a} ${b}» ou «${a} ${c}».`,
      soloPreguntar: 'Nesta página só é possível perguntar.', sinZona: 'Esta página não tem zona editável.', vacia: '(vazia)',
      firmado: (n) => `As suas intervenções serão assinadas como «${n}».`, anonima: 'As suas intervenções serão anônimas.',
      sinHistoria: 'Ainda não há intervenções.', sinPropuesta: 'Não há nenhuma proposta pendente.',
      publicando: 'Publicando a intervenção…',
      enRevision: 'Proposta enviada para revisão do CPE. Será publicada quando for aceita:',
      publicada: 'Intervenção publicada. Ficará visível para todos quando a implantação terminar (≈1 min):',
      descartada: 'Proposta descartada. A página volta ao estado anterior.',
      reescribiendo: 'O modelo está reescrevendo a página (pode levar até um minuto)…',
      vistaPrevia: (a, d) => `Pré-visualização aplicada. Escreva «${a}» para publicá-la ou «${d}» para voltar atrás.`,
      leyendo: 'Lendo…', video: 'vídeo', publicacion: 'publicação', textoCompleto: 'texto completo',
      soloTitulo: 'só título; sem transcrição', soloMetadatos: 'só metadados; sem texto completo',
      fuente: (tipo, titulo, base) => `Fonte: ${tipo} «${titulo}» (${base}).`,
      sinServidorAttr: 'O terminal não está ligado a nenhum servidor (falta data-servidor).',
      sinServidor: 'O terminal não está ligado a nenhum servidor.',
      sinContacto: 'Não foi possível contactar o servidor do terminal.', estadoServidor: (n) => `O servidor respondeu ${n}.`,
      fallo: 'Algo falhou.',
      bienvenidaEditable: 'Terminal dialético. Esta página é um espaço produzido coletivamente: pode transformá-la ou fazer-lhe perguntas.',
      bienvenidaPreguntar: 'Terminal dialético. Pergunte sobre esta página, as suas publicações ou os seus vídeos.',
      empezar: (c) => `Escreva «${c}» para começar.`,
      comandos: { ayuda: 'ajuda', limpiar: 'limpar', modo: 'modo', ver: 'ver', firma: 'assinar', historia: 'historico', aplicar: 'aplicar', descartar: 'descartar' },
      modosNombre: { preguntar: 'perguntar', intervenir: 'intervir' },
    },
    ru: {
      intervenir: '>_ Вмешаться', preguntar: '>_ Спросить',
      abrir: 'Открыть терминал (клавиша `)', nombre: 'Диалектический терминал', cerrar: 'Закрыть терминал',
      tituloEditable: 'Диалектический терминал — страница в процессе', tituloPreguntar: 'Диалектический терминал — вопросы',
      espacio: 'пространство', phIntervenir: 'опишите изменение или «?» + вопрос', phPreguntar: 'задайте вопрос об этой странице',
      btnPub: 'Объяснить выводы ▸', qPub: (t) => `Объясни основные выводы работы «${t}»`,
      btnVideo: 'О чём это? ▸', qVideo: (t) => `О чём видео «${t}»?`,
      ayudaEditable: [
        'Эта страница не закончена: любой может её преобразовать —',
        'её эстетику и организацию, не удаляя информацию.',
        'Опишите изменение, например:',
        '  «преврати главную страницу в хронологию исследования»',
        '  «перестрой карточки в одну типографскую колонку»',
        'Вы увидите предварительный просмотр. Затем:',
      ],
      ayudaPreguntar: 'Спрашивайте что угодно об этой странице, статье или видео.',
      dAplicar: 'опубликовать вмешательство (фиксируется в git)', dDescartar: 'вернуться к предыдущей версии',
      dHistoria: 'последние вмешательства', dVer: 'текущий HTML страницы', dFirma: 'подписывать вмешательства (пусто = анонимно)',
      argNombre: '<имя>', argPregunta: '<вопрос>', dPregunta: 'вопрос об этой странице, статье или видео',
      dModoPreguntar: 'всё, что вы напишете, будет вопросом', dModoIntervenir: 'снова преобразовывать страницу', dLimpiar: 'очистить терминал',
      modoFijado: (m) => `Режим: ${m}.`, modos: (a, b, c) => `Режимы: «${a} ${b}» или «${a} ${c}».`,
      soloPreguntar: 'На этой странице можно только задавать вопросы.', sinZona: 'На этой странице нет редактируемой зоны.', vacia: '(пусто)',
      firmado: (n) => `Ваши вмешательства будут подписаны как «${n}».`, anonima: 'Ваши вмешательства будут анонимными.',
      sinHistoria: 'Вмешательств пока нет.', sinPropuesta: 'Нет ожидающего предложения.',
      publicando: 'Публикация вмешательства…',
      enRevision: 'Предложение отправлено на рассмотрение CPE. Оно будет опубликовано после одобрения:',
      publicada: 'Вмешательство опубликовано. Оно станет видно всем после развёртывания (≈1 мин):',
      descartada: 'Предложение отклонено. Страница возвращается в прежнее состояние.',
      reescribiendo: 'Модель переписывает страницу (это может занять до минуты)…',
      vistaPrevia: (a, d) => `Просмотр применён. Введите «${a}», чтобы опубликовать, или «${d}», чтобы вернуться.`,
      leyendo: 'Читаю…', video: 'видео', publicacion: 'публикация', textoCompleto: 'полный текст',
      soloTitulo: 'только название; без расшифровки', soloMetadatos: 'только метаданные; без полного текста',
      fuente: (tipo, titulo, base) => `Источник: ${tipo} «${titulo}» (${base}).`,
      sinServidorAttr: 'Терминал не подключён к серверу (нет data-servidor).',
      sinServidor: 'Терминал не подключён к серверу.',
      sinContacto: 'Не удалось связаться с сервером терминала.', estadoServidor: (n) => `Сервер ответил ${n}.`,
      fallo: 'Что-то пошло не так.',
      bienvenidaEditable: 'Диалектический терминал. Эта страница — коллективно производимое пространство: вы можете преобразовать её или задать ей вопросы.',
      bienvenidaPreguntar: 'Диалектический терминал. Спрашивайте об этой странице, её публикациях или видео.',
      empezar: (c) => `Введите «${c}», чтобы начать.`,
      comandos: { ayuda: 'помощь', limpiar: 'очистить', modo: 'режим', ver: 'код', firma: 'подпись', historia: 'история', aplicar: 'применить', descartar: 'отменить' },
      modosNombre: { preguntar: 'вопросы', intervenir: 'вмешательство' },
    },
    zh: {
      intervenir: '>_ 介入', preguntar: '>_ 提问',
      abrir: '打开终端（按 ` 键）', nombre: '辩证终端', cerrar: '关闭终端',
      tituloEditable: '辩证终端 — 进行中的页面', tituloPreguntar: '辩证终端 — 提问',
      espacio: '空间', phIntervenir: '描述一项修改，或输入「?」+ 问题', phPreguntar: '就本页提出问题',
      btnPub: '解释主要发现 ▸', qPub: (t) => `请解释《${t}》的主要发现`,
      btnVideo: '内容是什么？▸', qVideo: (t) => `视频《${t}》讲的是什么？`,
      ayudaEditable: [
        '本页尚未完成：任何人都可以改造它的',
        '美学与组织方式，但不得删除信息。',
        '描述你想要的修改，例如：',
        '  「把首页改成研究的时间线」',
        '  「把卡片重新排成单列排版」',
        '你会先看到预览。然后：',
      ],
      ayudaPreguntar: '可以就本页、某篇论文或某个视频提出任何问题。',
      dAplicar: '发布本次介入（记录在 git 中）', dDescartar: '回到之前的版本',
      dHistoria: '最近的介入', dVer: '本页当前的 HTML', dFirma: '为你的介入署名（留空 = 匿名）',
      argNombre: '<名字>', argPregunta: '<问题>', dPregunta: '就本页、论文或视频提问',
      dModoPreguntar: '你输入的一切都将被视为问题', dModoIntervenir: '重新开始改造页面', dLimpiar: '清空终端',
      modoFijado: (m) => `模式：${m}。`, modos: (a, b, c) => `模式：「${a} ${b}」或「${a} ${c}」。`,
      soloPreguntar: '本页只能提问。', sinZona: '本页没有可编辑区域。', vacia: '（空）',
      firmado: (n) => `你的介入将署名为「${n}」。`, anonima: '你的介入将匿名。',
      sinHistoria: '暂无介入。', sinPropuesta: '没有待处理的提案。',
      publicando: '正在发布介入…',
      enRevision: '提案已提交 CPE 审核，通过后将发布：',
      publicada: '介入已发布。部署完成后（约 1 分钟）所有人都能看到：',
      descartada: '提案已放弃。页面恢复到之前的状态。',
      reescribiendo: '模型正在改写页面（可能需要一分钟）…',
      vistaPrevia: (a, d) => `预览已应用。输入「${a}」发布，或输入「${d}」返回。`,
      leyendo: '正在阅读…', video: '视频', publicacion: '出版物', textoCompleto: '全文',
      soloTitulo: '仅标题；无文字稿', soloMetadatos: '仅元数据；无全文',
      fuente: (tipo, titulo, base) => `来源：${tipo}《${titulo}》（${base}）。`,
      sinServidorAttr: '终端未连接任何服务器（缺少 data-servidor）。',
      sinServidor: '终端未连接任何服务器。',
      sinContacto: '无法连接终端服务器。', estadoServidor: (n) => `服务器返回 ${n}。`,
      fallo: '出现错误。',
      bienvenidaEditable: '辩证终端。本页是一个集体生产的空间：你可以改造它，也可以向它提问。',
      bienvenidaPreguntar: '辩证终端。可以就本页、其出版物或视频提问。',
      empezar: (c) => `输入「${c}」开始。`,
      comandos: { ayuda: '帮助', limpiar: '清空', modo: '模式', ver: '查看', firma: '署名', historia: '历史', aplicar: '发布', descartar: '放弃' },
      modosNombre: { preguntar: '提问', intervenir: '介入' },
    },
    ar: {
      intervenir: '>_ تدخّل', preguntar: '>_ اسأل',
      abrir: 'افتح الطرفية (مفتاح `)', nombre: 'الطرفية الجدلية', cerrar: 'أغلق الطرفية',
      tituloEditable: 'الطرفية الجدلية — صفحة قيد التشكّل', tituloPreguntar: 'الطرفية الجدلية — اسأل',
      espacio: 'فضاء', phIntervenir: 'صِف تغييرًا، أو «?» + سؤال', phPreguntar: 'اطرح سؤالًا عن هذه الصفحة',
      btnPub: 'اشرح النتائج ▸', qPub: (t) => `اشرح لي أهم نتائج «${t}»`,
      btnVideo: 'عمّ يتحدث؟ ▸', qVideo: (t) => `عمّ يتحدث فيديو «${t}»؟`,
      ayudaEditable: [
        'هذه الصفحة غير مكتملة: يمكن لأي شخص أن يحوّلها،',
        'في جمالياتها وتنظيمها، دون حذف أي معلومات.',
        'صِف التغيير، مثلًا:',
        '  «حوّل الصفحة الرئيسية إلى خط زمني للبحث»',
        '  «أعد ترتيب البطاقات في عمود طباعي واحد»',
        'سترى معاينة. بعد ذلك:',
      ],
      ayudaPreguntar: 'اسأل ما تشاء عن هذه الصفحة أو بحث أو فيديو.',
      dAplicar: 'ينشر التدخّل (يُسجَّل في git)', dDescartar: 'يعود إلى النسخة السابقة',
      dHistoria: 'آخر التدخّلات', dVer: 'شيفرة HTML الحالية للصفحة', dFirma: 'وقّع تدخّلاتك (فارغ = مجهول)',
      argNombre: '<الاسم>', argPregunta: '<السؤال>', dPregunta: 'سؤال عن هذه الصفحة أو بحث أو فيديو',
      dModoPreguntar: 'كل ما تكتبه سيُعامل كسؤال', dModoIntervenir: 'العودة إلى تحويل الصفحة', dLimpiar: 'يمسح الطرفية',
      modoFijado: (m) => `الوضع: ${m}.`, modos: (a, b, c) => `الأوضاع: «${a} ${b}» أو «${a} ${c}».`,
      soloPreguntar: 'في هذه الصفحة يمكنك طرح الأسئلة فقط.', sinZona: 'لا توجد منطقة قابلة للتعديل في هذه الصفحة.', vacia: '(فارغة)',
      firmado: (n) => `ستُوقَّع تدخّلاتك باسم «${n}».`, anonima: 'ستكون تدخّلاتك مجهولة.',
      sinHistoria: 'لا توجد تدخّلات بعد.', sinPropuesta: 'لا يوجد اقتراح معلّق.',
      publicando: 'جارٍ نشر التدخّل…',
      enRevision: 'أُرسل الاقتراح إلى CPE للمراجعة، وسيُنشر عند قبوله:',
      publicada: 'نُشر التدخّل. سيظهر للجميع عند انتهاء النشر (≈ دقيقة واحدة):',
      descartada: 'تم تجاهل الاقتراح. عادت الصفحة إلى حالتها السابقة.',
      reescribiendo: 'النموذج يعيد كتابة الصفحة (قد يستغرق ذلك دقيقة)…',
      vistaPrevia: (a, d) => `طُبّقت المعاينة. اكتب «${a}» لنشرها أو «${d}» للتراجع.`,
      leyendo: 'جارٍ القراءة…', video: 'فيديو', publicacion: 'منشور', textoCompleto: 'النص الكامل',
      soloTitulo: 'العنوان فقط؛ دون نص مفرَّغ', soloMetadatos: 'البيانات الوصفية فقط؛ دون النص الكامل',
      fuente: (tipo, titulo, base) => `المصدر: ${tipo} «${titulo}» (${base}).`,
      sinServidorAttr: 'الطرفية غير متصلة بأي خادم (data-servidor مفقود).',
      sinServidor: 'الطرفية غير متصلة بأي خادم.',
      sinContacto: 'تعذّر الاتصال بخادم الطرفية.', estadoServidor: (n) => `ردّ الخادم بالرمز ${n}.`,
      fallo: 'حدث خطأ ما.',
      bienvenidaEditable: 'الطرفية الجدلية. هذه الصفحة فضاء يُنتَج جماعيًا: يمكنك تحويلها أو طرح الأسئلة عليها.',
      bienvenidaPreguntar: 'الطرفية الجدلية. اسأل عن هذه الصفحة أو منشوراتها أو فيديوهاتها.',
      empezar: (c) => `اكتب «${c}» للبدء.`,
      comandos: { ayuda: 'مساعدة', limpiar: 'مسح', modo: 'وضع', ver: 'عرض', firma: 'توقيع', historia: 'السجل', aplicar: 'نشر', descartar: 'تجاهل' },
      modosNombre: { preguntar: 'سؤال', intervenir: 'تدخل' },
    },
  };

  const IDIOMA = (() => {
    const l = (document.documentElement.lang || 'es').toLowerCase().slice(0, 2);
    return Object.prototype.hasOwnProperty.call(TEXTOS, l) ? l : 'es';
  })();
  const T = TEXTOS[IDIOMA];
  const DIR = document.documentElement.dir === 'rtl' || IDIOMA === 'ar' ? 'rtl' : 'ltr';

  // Nombre escrito → comando canónico (español). Se aceptan el idioma de la página, el español y el inglés.
  const ALIAS_COMANDOS = {};
  const ALIAS_MODOS = {};
  for (const l of new Set(['es', 'en', IDIOMA])) {
    for (const [canon, nombre] of Object.entries(TEXTOS[l].comandos)) ALIAS_COMANDOS[nombre.toLowerCase()] = canon;
    for (const [canon, nombre] of Object.entries(TEXTOS[l].modosNombre)) ALIAS_MODOS[nombre.toLowerCase()] = canon;
  }
  // Variantes con tilde o sin ella.
  if (IDIOMA === 'pt') ALIAS_COMANDOS['histórico'] = 'historia';
  if (IDIOMA === 'ar') ALIAS_MODOS['تدخّل'] = 'intervenir';

  const C = T.comandos;
  const M = T.modosNombre;


  function paginaActual() {
    let ruta = decodeURIComponent(location.pathname);
    if (ruta.startsWith(RAIZ.pathname)) ruta = ruta.slice(RAIZ.pathname.length);
    ruta = ruta.replace(/^\/+/, '');
    return !ruta || ruta.endsWith('/') ? `${ruta}index.html` : ruta;
  }

  const PAGINA = paginaActual();
  const estado = {
    modo: 'preguntar',
    propuesta: null, // { cuerpo, css, token, modo }
    original: null, // { nodos, css } antes de la vista previa
    ocupado: false,
    historial: [],
    posicion: 0,
    firma: undefined,
  };

  // ── Zona editable en el DOM ─────────────────────────────────

  function marcadores() {
    let inicio = null;
    let fin = null;
    for (const n of document.body.childNodes) {
      if (n.nodeType !== Node.COMMENT_NODE) continue;
      const v = n.nodeValue.trim();
      if (v === 'ZONA-DIALECTICA:INICIO') inicio = n;
      if (v === 'ZONA-DIALECTICA:FIN') fin = n;
    }
    return inicio && fin ? { inicio, fin } : null;
  }

  function nodosZona() {
    const m = marcadores();
    const nodos = [];
    if (m) for (let n = m.inicio.nextSibling; n && n !== m.fin; n = n.nextSibling) nodos.push(n);
    return nodos;
  }

  function hojaPropia() {
    return document.getElementById('estilo-dialectico');
  }

  function sustituirZona(nodos, css) {
    const m = marcadores();
    if (!m) return;
    nodosZona().forEach((n) => n.remove());
    nodos.forEach((n) => m.fin.parentNode.insertBefore(n, m.fin));
    if (hojaPropia()) hojaPropia().textContent = css || '';
    document.body.classList.remove('menu-open');
    // Los scripts del sitio se enlazan a los elementos al cargar: se vuelven a ejecutar sobre los nuevos.
    REINICIAR.forEach((src) => {
      const s = document.createElement('script');
      s.src = `${new URL(src, RAIZ).href}?r=${Date.now()}`;
      s.onload = () => s.remove();
      document.body.append(s);
    });
    decorar();
    document.dispatchEvent(new CustomEvent('zona-dialectica:actualizada'));
  }

  function nodosDesdeHtml(html) {
    // El HTML llega saneado por el servidor y la política CSP de la página impide
    // ejecutar scripts en línea.
    const plantilla = document.createElement('template');
    plantilla.innerHTML = html;
    return [...plantilla.content.childNodes];
  }

  function htmlZonaActual() {
    return nodosZona()
      .map((n) => {
        if (n.nodeType !== Node.ELEMENT_NODE) return n.nodeType === Node.TEXT_NODE ? n.textContent : '';
        const copia = n.cloneNode(true);
        copia.querySelectorAll('.td-explicar').forEach((b) => b.remove());
        return copia.outerHTML;
      })
      .join('')
      .trim();
  }

  // ── Interfaz ────────────────────────────────────────────────

  const editable = Boolean(marcadores());
  estado.modo = editable ? 'intervenir' : 'preguntar';

  const boton = document.createElement('button');
  boton.type = 'button';
  boton.className = 'td-lanzador';
  boton.setAttribute('aria-expanded', 'false');
  boton.setAttribute('aria-controls', 'td-panel');
  boton.title = T.abrir;
  boton.textContent = editable ? T.intervenir : T.preguntar;
  boton.lang = IDIOMA;
  boton.dir = 'ltr';

  const panel = document.createElement('section');
  panel.id = 'td-panel';
  panel.className = 'td-panel';
  panel.hidden = true;
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', T.nombre);
  panel.lang = IDIOMA;
  panel.dir = DIR;

  const barra = document.createElement('header');
  barra.className = 'td-barra';
  const titulo = document.createElement('span');
  titulo.textContent = editable ? T.tituloEditable : T.tituloPreguntar;
  const cerrar = document.createElement('button');
  cerrar.type = 'button';
  cerrar.className = 'td-cerrar';
  cerrar.setAttribute('aria-label', T.cerrar);
  cerrar.textContent = '×';
  barra.append(titulo, cerrar);

  const registro = document.createElement('div');
  registro.className = 'td-registro';
  registro.setAttribute('role', 'log');
  registro.setAttribute('aria-live', 'polite');

  const formulario = document.createElement('form');
  formulario.className = 'td-linea';
  const indicador = document.createElement('label');
  indicador.className = 'td-indicador';
  indicador.htmlFor = 'td-entrada';
  const entrada = document.createElement('input');
  entrada.id = 'td-entrada';
  entrada.className = 'td-entrada';
  entrada.autocomplete = 'off';
  entrada.spellcheck = false;
  entrada.maxLength = 500;
  formulario.append(indicador, entrada);

  panel.append(barra, registro, formulario);
  document.body.append(boton, panel);

  function fijarModo(modo) {
    estado.modo = modo;
    indicador.textContent = modo === 'intervenir' ? `${T.espacio}:~$` : `${T.espacio}:~?`;
    entrada.placeholder = modo === 'intervenir' ? T.phIntervenir : T.phPreguntar;
  }
  fijarModo(estado.modo);

  function escribir(texto, clase) {
    const linea = document.createElement('div');
    linea.className = `td-l ${clase || ''}`;
    linea.dir = 'auto';
    linea.textContent = texto;
    registro.append(linea);
    registro.scrollTop = registro.scrollHeight;
    return linea;
  }

  function enlace(texto, url) {
    const linea = document.createElement('div');
    linea.className = 'td-l';
    if (/^https:\/\//.test(url)) {
      const a = document.createElement('a');
      a.href = url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.textContent = texto;
      linea.append(a);
    } else {
      linea.textContent = texto;
    }
    registro.append(linea);
    registro.scrollTop = registro.scrollHeight;
  }

  function abrir() {
    panel.hidden = false;
    boton.setAttribute('aria-expanded', 'true');
    entrada.focus();
  }

  function ocultar() {
    panel.hidden = true;
    boton.setAttribute('aria-expanded', 'false');
    boton.focus();
  }

  boton.addEventListener('click', () => (panel.hidden ? abrir() : ocultar()));
  cerrar.addEventListener('click', ocultar);
  document.addEventListener('keydown', (e) => {
    const escribiendo = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable;
    if ((e.key === '`' || e.key === 'º') && !escribiendo) {
      e.preventDefault();
      abrir();
    } else if (e.key === 'Escape' && !panel.hidden) {
      ocultar();
    }
  });

  entrada.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowUp' && estado.posicion > 0) {
      estado.posicion -= 1;
      entrada.value = estado.historial[estado.posicion];
      e.preventDefault();
    } else if (e.key === 'ArrowDown' && estado.posicion < estado.historial.length) {
      estado.posicion += 1;
      entrada.value = estado.historial[estado.posicion] || '';
      e.preventDefault();
    }
  });

  formulario.addEventListener('submit', (e) => {
    e.preventDefault();
    const texto = entrada.value.trim();
    if (!texto || estado.ocupado) return;
    estado.historial.push(texto);
    estado.posicion = estado.historial.length;
    entrada.value = '';
    escribir(`${indicador.textContent} ${texto}`, 'td-eco');
    ejecutar(texto);
  });

  // ── Botones «explicar» en publicaciones y vídeos ────────────

  function botonExplicar(etiqueta, pregunta, ancla) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'td-explicar';
    b.textContent = etiqueta;
    b.addEventListener('click', () => {
      abrir();
      if (estado.ocupado) return;
      escribir(`${T.espacio}:~? ${pregunta}`, 'td-eco');
      ejecutar(`?${pregunta}`, ancla);
    });
    return b;
  }

  function decorar() {
    document.querySelectorAll('article.pub[id]').forEach((art) => {
      if (art.querySelector('.td-explicar')) return;
      const t = art.querySelector('h3');
      if (!t) return;
      art.append(botonExplicar(T.btnPub, T.qPub(t.textContent.trim()), art.id));
    });
    document.querySelectorAll('figure.video').forEach((fig) => {
      if (fig.querySelector('.td-explicar')) return;
      const marco = fig.querySelector('iframe[src*="/embed/"]');
      const t = fig.querySelector('figcaption b');
      const id = marco && (marco.getAttribute('src').match(/\/embed\/([A-Za-z0-9_-]+)/) || [])[1];
      if (!id || !t) return;
      (fig.querySelector('figcaption') || fig).append(
        botonExplicar(T.btnVideo, T.qVideo(t.textContent.trim()), `video:${id}`),
      );
    });
  }

  // ── Comandos ────────────────────────────────────────────────

  function leerFirma() {
    if (estado.firma !== undefined) return estado.firma;
    try {
      return localStorage.getItem(CLAVE_FIRMA) || '';
    } catch (_) {
      return '';
    }
  }

  function guardarFirma(valor) {
    estado.firma = valor;
    try {
      if (valor) localStorage.setItem(CLAVE_FIRMA, valor);
      else localStorage.removeItem(CLAVE_FIRMA);
    } catch (_) {
      /* sin almacenamiento: la firma dura lo que dure la visita */
    }
  }

  const COMANDOS = {
    ayuda() {
      const fila = (cmd, desc) => `  ${cmd.padEnd(16)} ${desc}`;
      const lineas = editable
        ? [
            ...T.ayudaEditable,
            fila(C.aplicar, T.dAplicar),
            fila(C.descartar, T.dDescartar),
            fila(C.historia, T.dHistoria),
            fila(C.ver, T.dVer),
            fila(`${C.firma} ${T.argNombre}`, T.dFirma),
          ]
        : [T.ayudaPreguntar];
      [
        ...lineas,
        fila(`? ${T.argPregunta}`, T.dPregunta),
        editable ? fila(`${C.modo} ${M.preguntar}`, T.dModoPreguntar) : '',
        editable ? fila(`${C.modo} ${M.intervenir}`, T.dModoIntervenir) : '',
        fila(C.limpiar, T.dLimpiar),
      ]
        .filter(Boolean)
        .forEach((l) => escribir(l, 'td-tenue'));
    },
    limpiar() {
      registro.textContent = '';
    },
    modo(arg) {
      const modo = ALIAS_MODOS[arg.trim().toLowerCase()];
      if (modo === 'preguntar' || (modo === 'intervenir' && editable)) {
        fijarModo(modo);
        escribir(T.modoFijado(M[modo]));
      } else {
        escribir(editable ? T.modos(C.modo, M.preguntar, M.intervenir) : T.soloPreguntar, 'td-aviso');
      }
    },
    ver() {
      if (!editable) return escribir(T.sinZona, 'td-aviso');
      escribir(htmlZonaActual() || T.vacia, 'td-codigo');
    },
    firma(arg) {
      guardarFirma(arg.slice(0, 40));
      escribir(arg ? T.firmado(arg.slice(0, 40)) : T.anonima);
    },
    async historia() {
      const datos = await pedir('GET', `/historia?pagina=${encodeURIComponent(PAGINA)}`);
      if (!datos.intervenciones.length) return escribir(T.sinHistoria);
      datos.intervenciones.forEach((k) => {
        const fecha = k.fecha ? new Date(k.fecha).toLocaleString(IDIOMA) : '';
        enlace(`${k.sha}  ${fecha}  ${k.mensaje}`, k.url);
      });
    },
    async aplicar() {
      if (!estado.propuesta) return escribir('No hay ninguna propuesta pendiente.', 'td-aviso');
      escribir(T.publicando, 'td-tenue');
      const { cuerpo, css, token } = estado.propuesta;
      const r = await pedir('POST', '/aplicar', { cuerpo, css, token });
      estado.propuesta = null;
      estado.original = null;
      escribir(
        r.modo === 'revision'
          ? T.enRevision
          : T.publicada,
        'td-ok',
      );
      enlace(r.url, r.url);
    },
    descartar() {
      if (!estado.propuesta) return escribir('No hay ninguna propuesta pendiente.', 'td-aviso');
      sustituirZona(estado.original.nodos, estado.original.css);
      estado.propuesta = null;
      estado.original = null;
      escribir(T.descartada);
    },
  };

  async function proponer(instruccion) {
    if (estado.propuesta) {
      // Una instrucción nueva parte de la versión publicada, no de la vista previa.
      sustituirZona(estado.original.nodos, estado.original.css);
      estado.propuesta = null;
    }
    const espera = escribir(T.reescribiendo, 'td-tenue td-pulso');
    try {
      const r = await pedir('POST', '/proponer', { instruccion, pagina: PAGINA, firma: leerFirma() });
      const hoja = hojaPropia();
      estado.original = { nodos: nodosZona().map((n) => n.cloneNode(true)), css: hoja ? hoja.textContent : '' };
      estado.propuesta = r;
      sustituirZona(nodosDesdeHtml(r.cuerpo), r.css);
      (r.advertencias || []).forEach((a) => escribir(`! ${a}`, 'td-aviso'));
      escribir(T.vistaPrevia(C.aplicar, C.descartar), 'td-ok');
    } finally {
      espera.remove();
    }
  }

  async function preguntar(pregunta, ancla) {
    const espera = escribir(T.leyendo, 'td-tenue td-pulso');
    try {
      const r = await pedir('POST', '/preguntar', { pregunta, pagina: PAGINA, ancla: ancla || location.hash.slice(1) });
      if (r.fuente) {
        const tipo = r.fuente.tipo === 'video' ? T.video : T.publicacion;
        const base = r.fuente.textoCompleto ? T.textoCompleto : r.fuente.tipo === 'video' ? T.soloTitulo : T.soloMetadatos;
        escribir(T.fuente(tipo, r.fuente.titulo, base), 'td-tenue');
      }
      escribir(r.respuesta.replace(/\*\*/g, '').replace(/^#+\s*/gm, ''), 'td-respuesta');
    } finally {
      espera.remove();
    }
  }

  async function ejecutar(texto, ancla) {
    const [cabeza, ...resto] = texto.split(/\s+/);
    const nombre = Object.prototype.hasOwnProperty.call(ALIAS_COMANDOS, cabeza.toLowerCase()) ? ALIAS_COMANDOS[cabeza.toLowerCase()] : '';
    const comando = nombre ? COMANDOS[nombre] : null;
    const arg = resto.join(' ');
    estado.ocupado = true;
    entrada.disabled = true;
    try {
      if (comando && (nombre === 'firma' || nombre === 'modo' || !arg)) {
        await comando(arg);
      } else if (!SERVIDOR) {
        escribir(T.sinServidorAttr, 'td-error');
      } else if (texto.startsWith('?') || estado.modo === 'preguntar') {
        const pregunta = texto.replace(/^\?\s*/, '');
        if (pregunta) await preguntar(pregunta, ancla);
      } else {
        await proponer(texto);
      }
    } catch (e) {
      escribir(e.message || T.fallo, 'td-error');
    } finally {
      estado.ocupado = false;
      entrada.disabled = false;
      if (!panel.hidden) entrada.focus();
    }
  }

  async function pedir(metodo, ruta, cuerpo) {
    if (!SERVIDOR) throw new Error(T.sinServidor);
    let r;
    try {
      r = await fetch(SERVIDOR + ruta, {
        method: metodo,
        headers: cuerpo ? { 'Content-Type': 'application/json' } : {},
        body: cuerpo ? JSON.stringify(cuerpo) : undefined,
      });
    } catch (_) {
      throw new Error(T.sinContacto);
    }
    const datos = await r.json().catch(() => ({}));
    // Las operaciones largas responden 200 de inmediato y, si fallan, traen el error en el cuerpo.
    if (!r.ok || datos.error) throw new Error(datos.error || T.estadoServidor(r.status));
    return datos;
  }

  decorar();
  escribir(
    editable
      ? T.bienvenidaEditable
      : T.bienvenidaPreguntar,
    'td-tenue',
  );
  escribir(T.empezar(C.ayuda), 'td-tenue');
})();
