import { english } from './strings.js'

export const supportedLanguages = [
  { code: 'en', label: 'English', locale: 'en-ZA' },
  { code: 'zu', label: 'isiZulu', locale: 'zu-ZA' },
  { code: 'st', label: 'Sesotho', locale: 'st-ZA' },
]

const messages = {
  en: {
    navHome: 'Home', navAdd: 'Add', navForecast: 'Forecast', navSavings: 'Savings', navSettings: 'Settings',
    homeTitle: 'A little more breathing room.', homeSubtitle: 'Small moves today can make a tight week easier.',
    addTitle: 'Put it on the books.', addSubtitle: 'Keep the picture honest: add money as it comes and goes.',
    forecastTitle: 'See what’s coming.', forecastSubtitle: 'A guide from your entries, never a promise.',
    savingsTitle: 'Build your buffer.', savingsSubtitle: 'A steady set-aside can soften an uneven month.',
    settingsTitle: 'Your account.', settingsSubtitle: 'Your data belongs to you.',
    onboardingEyebrow: 'YOUR MONEY, WITH A PLAN', onboardingTitle: 'Make uneven income easier to plan.',
    onboardingDescription: 'Log what comes in and what goes out. Boloka helps you spot a possible tight week and plan a buffer, using estimates you can inspect.',
    onboardingStepOne: 'Record income as it arrives', onboardingStepTwo: 'Add bills and everyday costs', onboardingStepThree: 'See an explainable 30-day estimate',
    onboardingStart: 'Record your first income', onboardingPreview: 'Explore the sample dashboard', onboardingSignIn: 'Sign in or create an account',
    previewLabel: 'Sample preview', previewNotice: 'Sample preview. Numbers are fictional and changes stay in this browser session.',
    offlineTitle: 'You’re offline.', offlineBody: 'Sample mode still works. Account data and saved changes need a connection.',
    onlineTitle: 'Connection restored.', retry: 'Try again', dataSaver: 'Low-data mode', language: 'Language',
    amount: 'Amount', incomeSource: 'Where did it come from?', expenseCategory: 'What was it for?',
    receivedDate: 'Date received', paidDate: 'Date paid', recurring: 'It comes around regularly',
    saveIncome: 'Save income', saveExpense: 'Save expense', accountTitle: 'Your money stays yours.',
    email: 'Email address', password: 'Password', signIn: 'Sign in', createAccount: 'Create account',
    privateTitle: 'Private by design',
    scamTitle: 'A quick safety check', scamBody: 'Boloka will never ask for your bank PIN, password or one-time PIN (OTP). Stop and verify through your bank’s official app or number if anyone pressures you to share a code or move money.',
    showForecast: 'See the forecast', addEntry: 'Add an entry', firstEntry: 'Add your first entry',
  },
  zu: {
    navHome: 'Ikhaya', navAdd: 'Faka', navForecast: 'Isibikezelo', navSavings: 'Ukonga', navSettings: 'Izilungiselelo',
    homeTitle: 'Thola indawo yokuphefumula ngemali yakho.', homeSubtitle: 'Izinyathelo ezincane namuhla zingasiza ukwenza isonto elinzima libe lula.',
    addTitle: 'Bhala imali engenayo nephumayo.', addSubtitle: 'Bhala imali engenayo nephumayo ukuze ubone isimo sakho sangempela.',
    forecastTitle: 'Bona okuzayo.', forecastSubtitle: 'Lesi isiqondiso esisekelwe kulokho okubhalile, asisona isiqinisekiso.',
    savingsTitle: 'Yakha isikhwama sakho.', savingsSubtitle: 'Ukubeka imali eceleni njalo kungasiza ezinyangeni ezingalingani.',
    settingsTitle: 'I-akhawunti yakho.', settingsSubtitle: 'Idatha yakho ingeyakho.',
    onboardingEyebrow: 'IMALI YAKHO, NGESU', onboardingTitle: 'Hlela kangcono imali engenayo engalingani.',
    onboardingDescription: 'Bhala imali engenayo nephumayo. IBoloka ikusiza ukubona isonto elingase libe nzima nokuhlela imali ozoyibeka eceleni.',
    onboardingStepOne: 'Bhala imali engenayo uma ifika', onboardingStepTwo: 'Faka izikweletu nezindleko zansuku zonke', onboardingStepThree: 'Bona isilinganiso sezinsuku ezingu-30 esichazekayo',
    onboardingStart: 'Bhala imali yakho yokuqala engenayo', onboardingPreview: 'Buka isibonelo sedeshibhodi', onboardingSignIn: 'Ngena ngemvume noma dala i-akhawunti',
    previewLabel: 'Isibonelo', previewNotice: 'Lesi isibonelo. Izinombolo zingamanga futhi izinguquko zigcinwa kulesi siphequluli kuphela.',
    offlineTitle: 'Awuxhunyiwe ku-inthanethi.', offlineBody: 'Imodi yesibonelo isasebenza. Idatha ye-akhawunti nezinguquko ezigciniwe zidinga uxhumano.',
    onlineTitle: 'Uxhumano lubuyile.', retry: 'Zama futhi', dataSaver: 'Imodi yokonga idatha', language: 'Ulimi',
    highContrast: 'Umehluko ophezulu', highContrastHelp: 'Khulisa umehluko phakathi kombhalo, izilawuli nengemuva.',
    largerText: 'Umbhalo omkhulu', largerTextHelp: 'Khulisa umbhalo nezikhala ukuze kube lula ukufunda.',
    estimatedIncomeChart: 'Isilinganiso sokuhlelwa kwemali engenayo samasonto angu-{weeks}',
    amount: 'Inani', incomeSource: 'Livelaphi leli nani?', expenseCategory: 'Lisetshenziselweni?',
    receivedDate: 'Usuku olitholwe ngalo', paidDate: 'Usuku olukhokhwe ngalo', recurring: 'Liyaphindaphindeka njalo',
    saveIncome: 'Londoloza imali engenayo', saveExpense: 'Londoloza izindleko', accountTitle: 'Imali yakho ihlala ingeyakho.',
    email: 'Ikheli le-imeyili', password: 'Iphasiwedi', signIn: 'Ngena ngemvume', createAccount: 'Dala i-akhawunti',
    privateTitle: 'Kuvikelwe kusukela ekuqaleni',
    scamTitle: 'Hlola ukuphepha', scamBody: 'IBoloka ayisoze yacela i-PIN yasebhange, iphasiwedi noma i-PIN yesikhathi esisodwa (OTP). Yima uqinisekise ngohlelo lokusebenza noma inombolo esemthethweni yebhange lakho uma othile ekucindezela ukuthi wabelane ngekhodi noma uthumele imali.',
    showForecast: 'Bona isibikezelo', addEntry: 'Faka okufakiwe', firstEntry: 'Faka imali yakho yokuqala',
    editEntry: 'Hlela okufakiwe', edit: 'Hlela', delete: 'Susa', cancel: 'Khansela', saveChanges: 'Londoloza izinguquko',
    optionalNote: 'Inothi ongazikhethela', expenseDate: 'Usuku lokukhokha noma lokugcina', moneyIn: 'Imali engenayo', moneyOut: 'Imali ephumayo',
    recordedDates: 'Izinsuku ezirekhodiwe', showRecent: 'Bonisa okufakiwe kwakamuva', showLoadedEntries: 'Bonisa konke okufakiwe okulayishiwe',
    estimatedIncome: 'Imali engenayo elinganisiwe', possibleRange: 'Ububanzi besibonelo esiqanjiwe', weekNumber: 'Isigaba {number}',
    greeting: 'Kuhle ukukubona, {name}.', notAvailable: 'Akutholakali', dataControls: 'Ukulawula idatha yakho', exportLoaded: 'Khipha okufakiwe okulayishiwe (JSON)',
    yourMoneyOverview: 'Uhlolojikelele lwemali yakho', recordedBalance: 'ISAMBA ESIREKHODIWE', fromIncomeAndExpensesYouVeLogged: 'Kusukela emalini engenayo nasezindlekweni ozirekhodile',
    estimatedGap: 'IGEBE ELILINGANISIWE', recentMoney: 'Imali yakamuva', thisWeek: 'Kuleli sonto', incomeYouVeRecorded: 'Imali engenayo oyirekhodile',
    setAsideEachWeek: 'Beka eceleni isonto ngalinye', forecastConfidence: 'Izinga lokuthembeka kwesibikezelo', theLatest: 'OKWAKAMUVA', moneyMoves: 'Ukunyakaza kwemali', addOne: 'Faka okukodwa',
    yourStoryStartsHere: 'Indaba yakho iqala lapha.', oneSmallMove: 'ISINYATHELO ESINCANE', quickEntry: 'UKUFAKA OKUSHESHAYO', whatMoved: 'Yini eshintshile?', entryType: 'Uhlobo lokufakiwe',
    importIncome: 'Faka imali engenayo ngefayela', chooseACsvFile: 'Khetha ifayela le-CSV',
    next: 'OKULANDELAYO', days: 'IZINSUKU', expectedIncome: 'ISILINGANISO SEMALI ENGENAYO', knownCosts: 'IZINDLEKO EZIFAKIWE KULESI SILINGANISO', possibleGap: 'IGEBE ELINGASE LIBE KHONA',
    weekByWeek: 'ISONTO NGESONTO', incomeOutlook: 'Isimo semali engenayo', estimatedWeeklyIncome: 'Imali engenayo elinganisiwe ngesonto', noEstimateYet: 'Akukho silinganiso okwamanje.',
    yourWeeklyBuffer: 'ISIKHWAMA SAKHO SAMASONTO', recordMoneyYouVePutAside: 'Rekhoda imali oyibeke eceleni', dateSetAside: 'Usuku lokubeka eceleni', addToMyBuffer: 'Faka esikhwameni sami',
    recentSetAsides: 'Imali esanda kubekwa eceleni', remove: 'Susa', accountPrivacy: 'I-AKHAWUNTI NOKUPHEPHA KWEDATHA', signOut: 'Phuma', safety: 'UKUPHEPHA', mainNavigation: 'Ukuzulazula okuyinhloko',
    cashScenario: 'Imali etholakalayo manje (uyazikhethela, yalesi simo kuphela)', applyCashScenario: 'Sebenzisa lesi simo semali', cashScenarioFailed: 'Asikwazanga ukushintsha lesi simo. Isilinganiso sangaphambilini sisaboniswa.',
    forecastPeriod: 'Izinsuku ezingu-{days} ezizayo', samplePreviewOnly: 'Izinguquko zesibonelo zithinta izamba ezirekhodiwe kuphela.', dateHelp: 'Ngezindleko ezizayo, faka usuku okufanele zikhokhwe ngalo. Izindleko eziphindaphindayo zangaphambilini aziphindi ngokuzenzakalelayo.',
  },
  st: {
    navHome: 'Lehae', navAdd: 'Kenya', navForecast: 'Khakanyo', navSavings: 'Poloko', navSettings: 'Litlhophiso',
    homeTitle: 'Etsa hore chelete ea hao e u fe phomolo.', homeSubtitle: 'Mehato e menyenyane kajeno e ka nolofatsa beke e thata.',
    addTitle: 'Ngola chelete e kenang le e tsoang.', addSubtitle: 'Ngola chelete ha e kena le ha e tsoa hore setšoantšo se nepahale.',
    forecastTitle: 'Sheba se tlang.', forecastSubtitle: 'Ena ke tataiso e tsoang ho seo u se ngotseng, eseng tiisetso.',
    savingsTitle: 'Haha polokelo ea hao.', savingsSubtitle: 'Ho behella chelete ka thoko khafetsa ho ka thusa khoeling e sa tsitsang.',
    settingsTitle: 'Akhaonto ea hao.', settingsSubtitle: 'Lintlha tsa hao ke tsa hao.',
    onboardingEyebrow: 'CHELETE EA HAO, KA MORALO', onboardingTitle: 'Rera chelete e kenang e sa tsitsang habonolo.',
    onboardingDescription: 'Ngola chelete e kenang le e tsoang. Boloka e u thusa ho bona beke e ka bang thata le ho rera chelete ea polokelo ka likhakanyo tse hlakileng.',
    onboardingStepOne: 'Ngola chelete ha e fihla', onboardingStepTwo: 'Kenya likoloto le litšenyehelo tsa letsatsi le letsatsi', onboardingStepThree: 'Sheba khakanyo ea matsatsi a 30 e hlalosehang',
    onboardingStart: 'Ngola chelete ea hao ea pele', onboardingPreview: 'Sheba mohlala oa dashboard', onboardingSignIn: 'Kena kapa u thehe akhaonto',
    previewLabel: 'Mohlala', previewNotice: 'Ona ke mohlala. Lipalo ke tsa boiqapelo; liphetoho li lula sebatling sena feela.',
    offlineTitle: 'Ha ua hokeloa inthaneteng.', offlineBody: 'Mokhoa oa mohlala o ntse o sebetsa. Lintlha tsa akhaonto le liphetoho tse bolokiloeng li hloka khokahano.',
    onlineTitle: 'Khokahano e khutlile.', retry: 'Leka hape', dataSaver: 'Mokhoa oa ho boloka data', language: 'Puo',
    highContrast: 'Phapang e phahameng', highContrastHelp: 'Eketsa phapang pakeng tsa mongolo, ditaolo le bokamorao.',
    largerText: 'Mongolo o moholo', largerTextHelp: 'Holisa mongolo le likheo hore ho be bonolo ho bala.',
    estimatedIncomeChart: 'Tekanyetso ya moralo wa lekeno ya dibeke tse {weeks}',
    amount: 'Chelete', incomeSource: 'E tsoa hokae?', expenseCategory: 'E sebeliselitsoe eng?',
    receivedDate: 'Letsatsi leo e amohetsoeng ka lona', paidDate: 'Letsatsi leo e lefiloeng ka lona', recurring: 'E etsahala khafetsa',
    saveIncome: 'Boloka chelete e kenang', saveExpense: 'Boloka litšenyehelo', accountTitle: 'Chelete ea hao ke ea hao.',
    email: 'Aterese ea lengolo-tsoibila', password: 'Lekunutu', signIn: 'Kena', createAccount: 'Theha akhaonto',
    privateTitle: 'Tšireletso ke karolo ea moralo',
    scamTitle: 'Tlhahlobo e potlakileng ea tšireletso', scamBody: 'Boloka e ke ke ea u botsa PIN ea banka, password kapa PIN ea nako e le ’ngoe (OTP). Ema ’me u netefatse ka app kapa nomoro ea banka ea hao haeba motho a u potlakisetsa ho fana ka khoutu kapa ho romela chelete.',
    showForecast: 'Sheba khakanyo', addEntry: 'Kenya tlaleho', firstEntry: 'Kenya chelete ea pele',
    editEntry: 'Fetola tlaleho', edit: 'Fetola', delete: 'Hlakola', cancel: 'Khansela', saveChanges: 'Boloka liphetoho',
    optionalNote: 'Tlhokomeliso eo u ka e sieang', expenseDate: 'Letsatsi leo tefo e entsoeng kapa e lokelang ho etsoa ka lona', moneyIn: 'Chelete e kenang', moneyOut: 'Chelete e tsoang',
    recordedDates: 'Matsatsi a litlaleho', showRecent: 'Bontša litlaleho tsa morao tjena', showLoadedEntries: 'Bontša litlaleho tsohle tse laetsoeng',
    estimatedIncome: 'Chelete e kenang e hakantsoeng', possibleRange: 'Mefuta ea linomoro tsa mohlala oa boiqapelo', weekNumber: 'Karolo ea {number}',
    greeting: 'Ke thabela ho u bona, {name}.', notAvailable: 'Ha e fumanehe', dataControls: 'Taolo ea lintlha tsa hao', exportLoaded: 'Ntša litlaleho tse laetsoeng (JSON)',
    yourMoneyOverview: 'Kakaretso ea chelete ea hao', recordedBalance: 'KAKARETSO E NGOLISITSOENG', fromIncomeAndExpensesYouVeLogged: 'Ho tsoa cheleteng e kenang le litšenyehelong tseo u li ngotseng',
    estimatedGap: 'KHAFA E HAKANTSOENG', recentMoney: 'Chelete ea morao tjena', thisWeek: 'Bekeng ena', incomeYouVeRecorded: 'Chelete e kenang eo u e ngotseng',
    setAsideEachWeek: 'Behella ka thoko beke le beke', forecastConfidence: 'Tšepo ea khakanyo', theLatest: 'TSE NCHA KA HO FETISISA', moneyMoves: 'Tsamaiso ea chelete', addOne: 'Kenya e le ’ngoe',
    yourStoryStartsHere: 'Pale ea hao e qala mona.', oneSmallMove: 'MOHATO O MONG O MONYENYANE', quickEntry: 'HO KENYA KA POTLAKO', whatMoved: 'Ho fetohile eng?', entryType: 'Mofuta oa tlaleho',
    importIncome: 'Kenya chelete e kenang ka faele', chooseACsvFile: 'Khetha faele ea CSV',
    next: 'E LATELANG', days: 'MATSATSI', expectedIncome: 'KHAKANYO EA CHELETE E KENANG', knownCosts: 'LITŠENYEHELO TSE KENYELLELITSOENG KHAKANYONG ENA', possibleGap: 'KHAFA E KA BANG TENG',
    weekByWeek: 'BEKE LE BEKE', incomeOutlook: 'Pono ea chelete e kenang', estimatedWeeklyIncome: 'Chelete e kenang e hakantsoeng ka beke', noEstimateYet: 'Ha ho khakanyo hona joale.',
    yourWeeklyBuffer: 'POLOKELO EA HAO EA BEKE LE BEKE', recordMoneyYouVePutAside: 'Ngola chelete eo u e behetseng ka thoko', dateSetAside: 'Letsatsi leo e behetsoeng ka thoko ka lona', addToMyBuffer: 'Kenya polokelong ea ka',
    recentSetAsides: 'Chelete e sa tsoa behelloa ka thoko', remove: 'Tlosa', accountPrivacy: 'AKHAONTO LE TŠIRELETSO EA LINTLHA', signOut: 'Tsoa', safety: 'TŠIRELETSO', mainNavigation: 'Tsamaiso e kholo',
    cashScenario: 'Chelete e teng hona joale (ka boikhethelo, bakeng sa boemo bona feela)', applyCashScenario: 'Sebelisa boemo bona ba chelete', cashScenarioFailed: 'Ha rea khona ho fetola boemo bona. Khakanyo e fetileng e ntse e bontšoa.',
    forecastPeriod: 'Matsatsi a {days} a tlang', samplePreviewOnly: 'Liphetoho tsa mohlala li ama lipalo tse tlalehiloeng feela.', dateHelp: 'Bakeng sa litšenyehelo tse tlang, kenya letsatsi leo li lokelang ho lefshoa ka lona. Litšenyehelo tsa nako e fetileng tse pheta-phetoang ha li phetoe ka bohona.',
  },
}

Object.assign(messages.en, english)

export const translationKeys = Object.keys(messages.en)

export function missingTranslations(language) {
  return Object.keys(messages.en).filter(key => !Object.hasOwn(messages[language] || {}, key))
}

export function translate(language, key, variables = {}) {
  const value = messages[language]?.[key] ?? messages.en[key] ?? key
  return value.replace(/\{(\w+)\}/g, (match, name) => variables[name] == null ? match : String(variables[name]))
}

export function languageLocale(language) {
  return supportedLanguages.find((item) => item.code === language)?.locale ?? 'en-ZA'
}
