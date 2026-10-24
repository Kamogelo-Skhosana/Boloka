# Localization review inventory

The main React screens, accessible labels, chart copy, confirmations and action errors use translation keys. Existing isiZulu/Sesotho strings are drafts, not approved translations. New English strings deliberately fall back in both locales; no new wording was guessed. A visible language-draft notice explains the fallback. Dynamic values use named placeholders rather than stitched sentence fragments. Brand names, CSV column names and user-entered labels are not translated.

## Fluent-speaker acceptance

Review financial meanings (recorded net versus available cash, conditional gap, confidence, due costs and savings), action errors, delete confirmation, screen-reader labels, date/currency formatting, and interpolation order. Verify cancellation and destructive actions on a phone. Do not treat an English fallback as completed localization. Auth-provider/database errors are replaced with catalogued action messages; backend diagnostic prose remains English for API clients.

## Missing isiZulu and Sesotho copy

| Key | English source | isiZulu | Sesotho |
| --- | --- | --- | --- |
| aSmallCushionBuiltAtYourPace | A small cushion, built at your pace. | English fallback; review needed | English fallback; review needed |
| aWeekCouldHelpBuildABuffer | a week could help build a buffer. | English fallback; review needed | English fallback; review needed |
| accountPrivacy | ACCOUNT & PRIVACY | English fallback; review needed | English fallback; review needed |
| accountSignInWillBeAvailableWhenThe | Account sign-in will be available when the team connects the Supabase project. | English fallback; review needed | English fallback; review needed |
| addEntriesToSeeASetAsideSuggestion | Add entries to see a set-aside suggestion. | English fallback; review needed | English fallback; review needed |
| addIncomeAndExpenseEntriesToBuildYour | Add income and expense entries to build your estimate. | English fallback; review needed | English fallback; review needed |
| addIncomeEntriesToCreateAWeeklyOutlook | Add income entries to create a weekly outlook. | English fallback; review needed | English fallback; review needed |
| addIncomeOrABillToGetA | Add income or a bill to get a picture that’s yours. | English fallback; review needed | English fallback; review needed |
| addOne | Add one | English fallback; review needed | English fallback; review needed |
| addToMyBuffer | Add to my buffer | English fallback; review needed | English fallback; review needed |
| addedToThisSamplePreviewOnlySignIn | Added to this sample preview only. Sign in to save entries to your account. | English fallback; review needed | English fallback; review needed |
| addedToThisSamplePreviewOnlySignIn2 | Added to this sample preview only. Sign in to keep the contribution in your account. | English fallback; review needed | English fallback; review needed |
| alreadyHaveAnAccountSignIn | Already have an account? Sign in | English fallback; review needed | English fallback; review needed |
| and | , and | English fallback; review needed | English fallback; review needed |
| applyCashScenario | Apply cash scenario | English fallback; review needed | English fallback; review needed |
| boloka | boloka | English fallback; review needed | English fallback; review needed |
| bolokaHome | Boloka home | English fallback; review needed | English fallback; review needed |
| bolokaNeverAsksForYourBankPasswordYour | Boloka never asks for your bank password. Your entries are protected by account sign-in and row-level security. | English fallback; review needed | English fallback; review needed |
| bufferEmergencyFund | Buffer, emergency fund… | English fallback; review needed | English fallback; review needed |
| cancel | Cancel | English fallback; review needed | English fallback; review needed |
| cashAssumption | Available cash is unknown. This planning estimate assumes no cash is available. Recorded net income is not your bank balance. | English fallback; review needed | English fallback; review needed |
| cashScenario | Available cash now (optional, scenario only) | English fallback; review needed | English fallback; review needed |
| cashScenarioFailed | Could not update the scenario. The previous estimate is still shown. | English fallback; review needed | English fallback; review needed |
| cashScenarioHelp | Enter money you can use for these costs. This value is not bank verified, saved or included in exports. | English fallback; review needed | English fallback; review needed |
| cashScenarioUsed | This planning estimate uses the available cash you entered: {amount}. | English fallback; review needed | English fallback; review needed |
| chartAssumption | Seven-day planning blocks; the final block may be shorter. No calibrated confidence range is shown for account estimates. | English fallback; review needed | English fallback; review needed |
| checkInputs | Check your upcoming costs and cash. | English fallback; review needed | English fallback; review needed |
| checkYourInboxToConfirmYourEmailThen | Check your inbox to confirm your email, then sign in. | English fallback; review needed | English fallback; review needed |
| checkingYourAccountSecurely | Checking your account securely… | English fallback; review needed | English fallback; review needed |
| chooseACsvFile | Choose a CSV file | English fallback; review needed | English fallback; review needed |
| chooseACsvFileSmallerThan2Mb | Choose a CSV file smaller than 2 MB. | English fallback; review needed | English fallback; review needed |
| conditionalGap | Check this planning gap. | English fallback; review needed | English fallback; review needed |
| conditionalSuggestion | A conditional allocation, not proof that money is available to save. | English fallback; review needed | English fallback; review needed |
| confirmDelete | Delete {label}, {amount}, dated {date}? This cannot be undone. | English fallback; review needed | English fallback; review needed |
| couldNotImportThatFile | Could not import that file. | English fallback; review needed | English fallback; review needed |
| couldNotRemoveThatSetAsideTryAgain | Could not remove that set-aside. Try again. | English fallback; review needed | English fallback; review needed |
| couldNotSaveThatSetAsideTryAgain | Could not save that set-aside. Try again. | English fallback; review needed | English fallback; review needed |
| couldNotSaveThisEntryTryAgain | Could not save this entry. Try again. | English fallback; review needed | English fallback; review needed |
| createAnAccountToSaveYourEntriesPrivately | Create an account to save your entries privately. | English fallback; review needed | English fallback; review needed |
| csvInstructions | Use CSV columns amount, source, received_on and optional note. Dates use YYYY-MM-DD. | English fallback; review needed | English fallback; review needed |
| dataControls | Your data controls | English fallback; review needed | English fallback; review needed |
| dateHelp | For an upcoming cost, enter its due date. Past recurring costs are not automatically repeated. | English fallback; review needed | English fallback; review needed |
| dateSetAside | Date set aside | English fallback; review needed | English fallback; review needed |
| datesMustUseYyyyMmDd | . Dates must use YYYY-MM-DD. | English fallback; review needed | English fallback; review needed |
| days | DAYS | English fallback; review needed | English fallback; review needed |
| delete | Delete | English fallback; review needed | English fallback; review needed |
| deleteAccountDecision | Self-service account deletion is not available yet. Before launch, the team must define identity verification, deletion of stored records, backup retention and a published contact route. Removing entries or signing out does not delete your account. | English fallback; review needed | English fallback; review needed |
| deleteNamedEntry | Delete {label}, {amount}, {date} | English fallback; review needed | English fallback; review needed |
| deliveryShiftMarketOrder | Delivery shift, market order… | English fallback; review needed | English fallback; review needed |
| dismissMessage | Dismiss message | English fallback; review needed | English fallback; review needed |
| edit | Edit | English fallback; review needed | English fallback; review needed |
| editEntry | Edit entry | English fallback; review needed | English fallback; review needed |
| editNamedEntry | Edit {label}, {amount}, {date} | English fallback; review needed | English fallback; review needed |
| enterAnAmountGreaterThanR000 | Enter an amount greater than R0.00. | English fallback; review needed | English fallback; review needed |
| entryChangeFailed | Could not change the entry. Your existing record is unchanged. Check your connection and try again. | English fallback; review needed | English fallback; review needed |
| entryCorrected | Entry corrected. | English fallback; review needed | English fallback; review needed |
| entryDeleted | Entry deleted. | English fallback; review needed | English fallback; review needed |
| entrySavedToYourAccount | Entry saved to your account. | English fallback; review needed | English fallback; review needed |
| entryType | Entry type | English fallback; review needed | English fallback; review needed |
| estimatedGap | ESTIMATED GAP | English fallback; review needed | English fallback; review needed |
| estimatedIncome | Estimated income | English fallback; review needed | English fallback; review needed |
| estimatedIncomeChart | Income planning estimate | English fallback; review needed | English fallback; review needed |
| estimatedWeeklyIncome | Estimated weekly income | English fallback; review needed | English fallback; review needed |
| expectedIncome | INCOME ESTIMATE | English fallback; review needed | English fallback; review needed |
| expense | Expense | English fallback; review needed | English fallback; review needed |
| expenseDate | Date paid or due | English fallback; review needed | English fallback; review needed |
| exportLoaded | Export loaded entries (JSON) | English fallback; review needed | English fallback; review needed |
| exportScope | This download contains only entries currently loaded in the app, not a complete account export. Keep it private on shared devices. Sample exports are marked fictional. | English fallback; review needed | English fallback; review needed |
| forExampleRentOrAMonthlyPhoneBill | For example, rent or a monthly phone bill | English fallback; review needed | English fallback; review needed |
| forecastConfidence | Forecast confidence | English fallback; review needed | English fallback; review needed |
| forecastMethod | The income estimate uses {weeks} completed weeks (up to eight), including weeks with no recorded earnings. Spending records span {days} days. At least two completed weeks are needed for an income estimate, and six plus an expense basis for a planning gap. | English fallback; review needed | English fallback; review needed |
| forecastPeriod | Next {days} days | English fallback; review needed | English fallback; review needed |
| forecastTiming | Weekly earnings do not tell us when your next payout will arrive. No exact shortfall date or probability is predicted. | English fallback; review needed | English fallback; review needed |
| fromIncomeAndExpensesYouVeLogged | From income and expenses you’ve logged | English fallback; review needed | English fallback; review needed |
| gettingYourMoneyPictureReady | Getting your money picture ready. | English fallback; review needed | English fallback; review needed |
| giveYourNextWeekAHeadStart | Give your next week a head start. | English fallback; review needed | English fallback; review needed |
| greeting | Good to see you, {name}. | English fallback; review needed | English fallback; review needed |
| importIncome | Import income | English fallback; review needed | English fallback; review needed |
| importIncomeFromACsv | Import income from a CSV | English fallback; review needed | English fallback; review needed |
| importResult | Imported {imported} entries. {skipped} rows were skipped. | English fallback; review needed | English fallback; review needed |
| imported | Imported  | English fallback; review needed | English fallback; review needed |
| income | Income | English fallback; review needed | English fallback; review needed |
| incomeOutlook | Income outlook | English fallback; review needed | English fallback; review needed |
| incomeYouVeRecorded | Income you’ve recorded | English fallback; review needed | English fallback; review needed |
| incompleteHistory | Missing entries can change this estimate. Confidence has not been validated. | English fallback; review needed | English fallback; review needed |
| knownCosts | COSTS IN THIS ESTIMATE | English fallback; review needed | English fallback; review needed |
| loadFailed | Could not refresh account records. Check your connection and try again. | English fallback; review needed | English fallback; review needed |
| loadingDashboard | Loading dashboard | English fallback; review needed | English fallback; review needed |
| loadingForecastChart | Loading forecast chart… | English fallback; review needed | English fallback; review needed |
| loadingYourMoneyPicture | Loading your money picture… | English fallback; review needed | English fallback; review needed |
| mainNavigation | Main navigation | English fallback; review needed | English fallback; review needed |
| moneyIn | Money in | English fallback; review needed | English fallback; review needed |
| moneyMoves | Money moves | English fallback; review needed | English fallback; review needed |
| moneyOut | Money out | English fallback; review needed | English fallback; review needed |
| newToBolokaCreateAnAccount | New to Boloka? Create an account | English fallback; review needed | English fallback; review needed |
| next | NEXT | English fallback; review needed | English fallback; review needed |
| noEstimateYet | No estimate yet. | English fallback; review needed | English fallback; review needed |
| noSetAsidesRecordedYetYouCanStart | No set-asides recorded yet. You can start with any amount that feels manageable. | English fallback; review needed | English fallback; review needed |
| notAvailable | Not available | English fallback; review needed | English fallback; review needed |
| notEstablished | Not established | English fallback; review needed | English fallback; review needed |
| oneSmallMove | ONE SMALL MOVE | English fallback; review needed | English fallback; review needed |
| openAccountSettings | Open account settings | English fallback; review needed | English fallback; review needed |
| optionalNote | Optional note | English fallback; review needed | English fallback; review needed |
| planningEstimate | A conditional planning estimate | English fallback; review needed | English fallback; review needed |
| planningIntro | Record your earnings and upcoming costs. Inspect a planning estimate, the history it uses and the assumptions behind it. | English fallback; review needed | English fallback; review needed |
| possibleGap | POSSIBLE GAP | English fallback; review needed | English fallback; review needed |
| possibleRange | Fictional sample range | English fallback; review needed | English fallback; review needed |
| quickEntry | QUICK ENTRY | English fallback; review needed | English fallback; review needed |
| receivedOn | received_on | English fallback; review needed | English fallback; review needed |
| recentMoney | Recent money | English fallback; review needed | English fallback; review needed |
| recentSetAsides | Recent set-asides | English fallback; review needed | English fallback; review needed |
| recordMoneyYouVePutAside | Record money you’ve put aside | English fallback; review needed | English fallback; review needed |
| recordedBalance | RECORDED NET | English fallback; review needed | English fallback; review needed |
| recordedDates | Dates from recorded entries | English fallback; review needed | English fallback; review needed |
| recordedThisMonth | Recorded set-asides this month | English fallback; review needed | English fallback; review needed |
| recurringAssumption | Enter upcoming bills with their due dates. A recurring checkbox alone does not establish a repeat date; past recurring bills are not automatically repeated. | English fallback; review needed | English fallback; review needed |
| remove | Remove | English fallback; review needed | English fallback; review needed |
| removeContributionLabel | Remove set-aside {amount}, dated {date} | English fallback; review needed | English fallback; review needed |
| removeSetAside | Remove set-aside  | English fallback; review needed | English fallback; review needed |
| safety | SAFETY | English fallback; review needed | English fallback; review needed |
| sampleForecastStatic | This fictional recommendation does not recalculate when you add, edit or delete preview entries. Only recorded totals change. It is not a recommendation for your finances. | English fallback; review needed | English fallback; review needed |
| samplePreviewOnly | Preview changes affect recorded totals only. | English fallback; review needed | English fallback; review needed |
| sampleRecommendation | Fictional reference estimate | English fallback; review needed | English fallback; review needed |
| sampleReference | Sample recommendation, unchanged by preview edits | English fallback; review needed | English fallback; review needed |
| saveChanges | Save changes | English fallback; review needed | English fallback; review needed |
| saveFailed | Could not save the record. Check the fields and your connection, then try again. | English fallback; review needed | English fallback; review needed |
| savedReloadFailed | Saved, but the updated records could not be reloaded. Use Try again to refresh; do not submit the same record twice. | English fallback; review needed | English fallback; review needed |
| savingsNotCash | These records track money you put aside. They are not a verified savings balance or progress against a dated goal. | English fallback; review needed | English fallback; review needed |
| seeYourBuffer | See your buffer | English fallback; review needed | English fallback; review needed |
| setAsideALittleWhenAPayoutLands | Set aside a little when a payout lands. It can make a slower week feel less sudden. | English fallback; review needed | English fallback; review needed |
| setAsideEachWeek | Set aside each week | English fallback; review needed | English fallback; review needed |
| setAsideRemoved | Set-aside removed. | English fallback; review needed | English fallback; review needed |
| showLoadedEntries | Show all loaded entries | English fallback; review needed | English fallback; review needed |
| showRecent | Show recent entries | English fallback; review needed | English fallback; review needed |
| signInAndChooseACsvFileTo | Sign in and choose a CSV file to import income. | English fallback; review needed | English fallback; review needed |
| signInFailed | Sign-in could not be completed. Check the email, password and confirmation status, then try again. | English fallback; review needed | English fallback; review needed |
| signInToImportEntriesToYourAccount | Sign in to import entries to your account. | English fallback; review needed | English fallback; review needed |
| signInToSeeYourPrivateDashboard | Sign in to see your private dashboard. | English fallback; review needed | English fallback; review needed |
| signInToYourAccount | Sign in to your account | English fallback; review needed | English fallback; review needed |
| signOut | Sign out | English fallback; review needed | English fallback; review needed |
| signOutFailed | Could not sign out. Check your connection and try again. | English fallback; review needed | English fallback; review needed |
| skipToMainContent | Skip to main content | English fallback; review needed | English fallback; review needed |
| source | source | English fallback; review needed | English fallback; review needed |
| theLatest | THE LATEST | English fallback; review needed | English fallback; review needed |
| thisIsAnEstimateFromTheEntriesYou | This is an estimate from the entries you’ve recorded. It is not financial advice and cannot guarantee what you’ll earn or spend. | English fallback; review needed | English fallback; review needed |
| thisWeek | This week | English fallback; review needed | English fallback; review needed |
| translationReview | Language draft: some text is shown in English. isiZulu and Sesotho wording, including financial terms and confirmations, needs fluent-speaker review. | English fallback; review needed | English fallback; review needed |
| transportRent | Transport, rent… | English fallback; review needed | English fallback; review needed |
| unvalidated | Unvalidated | English fallback; review needed | English fallback; review needed |
| updatingYourMoneyPicture | Updating your money picture… | English fallback; review needed | English fallback; review needed |
| useColumns | Use columns | English fallback; review needed | English fallback; review needed |
| useRandsAndCentsForExample15000 | Use rands and cents, for example 150.00 | English fallback; review needed | English fallback; review needed |
| useSmallerTextOnlyForecastVisualsAndAsk | Use smaller text-only forecast visuals and ask the API to reduce transfer when supported. | English fallback; review needed | English fallback; review needed |
| weCouldNotCheckYourAccountCheckYour | We could not check your account. Check your connection and reload. | English fallback; review needed | English fallback; review needed |
| weCouldNotLoadYourMoneyPictureTry | We could not load your money picture. Try again. | English fallback; review needed | English fallback; review needed |
| weCouldNotReachSignInCheckYour | We could not reach sign-in. Check your connection and try again. | English fallback; review needed | English fallback; review needed |
| weCouldnTRefreshYourAccountData | We couldn’t refresh your account data. | English fallback; review needed | English fallback; review needed |
| week | Week  | English fallback; review needed | English fallback; review needed |
| weekByWeek | WEEK BY WEEK | English fallback; review needed | English fallback; review needed |
| weekNumber | Block {number} | English fallback; review needed | English fallback; review needed |
| weeklyForecastValues | Weekly forecast values | English fallback; review needed | English fallback; review needed |
| whatMoved | What moved? | English fallback; review needed | English fallback; review needed |
| youAreOfflineReconnectBeforeImportingToYour | You are offline. Reconnect before importing to your account. | English fallback; review needed | English fallback; review needed |
| youAreOfflineReconnectBeforeRemovingThisContribution | You are offline. Reconnect before removing this contribution. | English fallback; review needed | English fallback; review needed |
| youAreOfflineReconnectBeforeSavingThisContribution | You are offline. Reconnect before saving this contribution. | English fallback; review needed | English fallback; review needed |
| youAreOfflineReconnectBeforeSavingToYour | You are offline. Reconnect before saving to your account. | English fallback; review needed | English fallback; review needed |
| youHaveBeenSignedOut | You have been signed out. | English fallback; review needed | English fallback; review needed |
| youReSignedInYourPrivateMoneyPicture | You’re signed in. Your private money picture is ready. | English fallback; review needed | English fallback; review needed |
| yourEntriesStayPrivateToYourAccountPreview | Your entries stay private to your account. Preview entries are not uploaded. | English fallback; review needed | English fallback; review needed |
| yourMoneyOverview | Your money overview | English fallback; review needed | English fallback; review needed |
| yourSetAsideWasAddedToThisMonth | Your set-aside was added to this month’s buffer progress. | English fallback; review needed | English fallback; review needed |
| yourStoryStartsHere | Your story starts here. | English fallback; review needed | English fallback; review needed |
| yourWeeklyBuffer | YOUR WEEKLY BUFFER | English fallback; review needed | English fallback; review needed |
| spendingAssumption | Everyday spending is estimated only when recent records span at least 14 days. Otherwise this total includes only explicit upcoming entries; other costs remain unknown. | English fallback; review needed | English fallback; review needed |
| spendingOverlap | Some upcoming costs may already be included in the everyday spending estimate. The combined total is a conservative scenario. No gap or set-aside recommendation is available until these costs can be distinguished. | English fallback; review needed | English fallback; review needed |
| csvImportLimits | Use UTF-8, at most 2 MB and 10,000 rows. Amounts use a dot and at most two decimal places. Reimporting a file adds duplicates; review existing entries first. | English fallback; review needed | English fallback; review needed |
| csvErrors | First skipped-row errors (English diagnostics) | English fallback; review needed | English fallback; review needed |
| csvRowError | Line {line}: {message} | English fallback; review needed | English fallback; review needed |

## Existing translated keys

Ticket #20 adds English fallback keys requiring fluent isiZulu/Sesotho review:
`explainCalculation`, `explainHorizon`, `explainIncomeMath`, `explainUnknownIncome`,
`explainCostsMath`, `explainUnknownCash`, `explainGapMath`, `explainWeeklyMath`,
`explainOverlap`, `explainIncomeHistory`, `explainCostHistory`, `explainPlanningGap`,
`explainNoGap`, `explainUnavailable`. Review the distinction between recorded
income, estimated earnings, assumed cash, an aggregate gap and affordability.
Preserve named placeholders and the meaning of rounding; do not imply timing or
validated accuracy. No new translation has been guessed or approved.

All existing translated keys require review too, particularly onboarding, privacy claims, recurring costs and scam warnings. Their presence is not evidence of language quality. Do not mark issue #28 complete until fluent reviewers approve the financial and destructive-action flows.
