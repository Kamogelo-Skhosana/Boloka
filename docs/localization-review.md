# Localization review inventory

The main React screens, accessible labels, chart copy, confirmations and action errors use translation keys. Existing and supplemental isiZulu/Sesotho strings are drafts, not approved translations. Some newer and detailed copy still falls back to English; the visible notice explains this. Dynamic values use named placeholders rather than stitched sentence fragments. Brand names, CSV column names and user-entered labels are not translated. Review every translated value with fluent speakers before release.

## Fluent-speaker acceptance

Review financial meanings (recorded net versus available cash, conditional gap, confidence, due costs and savings), action errors, delete confirmation, screen-reader labels, date/currency formatting, and interpolation order. Verify cancellation and destructive actions on a phone. Do not treat an English fallback as completed localization. Auth-provider/database errors are replaced with catalogued action messages; backend diagnostic prose remains English for API clients.

## Missing isiZulu and Sesotho copy

The table below lists keys that currently fall back to English. Filled-in translations also need fluent review; presence in the catalog does not mean approval.

| Key | English source | isiZulu | Sesotho |
| --- | --- | --- | --- |
| startNextSteps | Build your planning picture | English fallback; review needed | English fallback; review needed |
| startRecordIncome | Record payouts you actually received, including earlier dates you can verify. A set-aside estimate needs six completed calendar weeks; check that weeks with no entries really are complete. Do not add invented earnings to fill gaps. | English fallback; review needed | English fallback; review needed |
| startAddCosts | Add the bills you know are coming with their actual due dates. You can plan around these without guessing future income. Past recurring flags do not add future bills automatically. | English fallback; review needed | English fallback; review needed |
| startReviewCosts | Check whether upcoming one-off costs are already covered by the everyday spending estimate. Until they can be distinguished, use the entries as a checklist rather than a set-aside recommendation. | English fallback; review needed | English fallback; review needed |
| startCheckCash | If you know the cash available for these costs, enter it in the optional cash scenario below. Include only money available to spend; recorded net income and savings contributions are not a bank balance. You can leave this unknown. | English fallback; review needed | English fallback; review needed |
| explainCalculation | How this estimate is calculated | English fallback; review needed | English fallback; review needed |
| explainHorizon | Included dates: {start} through {end}. | English fallback; review needed | English fallback; review needed |
| explainIncomeMath | Income: {total} recorded across {historyDays} completed calendar days, divided by {historyDays}, then multiplied by {days} days = {estimate}, rounded to cents. Weeks without recorded income count as zero. | English fallback; review needed | English fallback; review needed |
| explainUnknownIncome | Income is unknown: fewer than two completed weeks are available. No income estimate is calculated. | English fallback; review needed | English fallback; review needed |
| explainCostsMath | Costs: {scheduled} in dated upcoming entries + {everyday} in estimated everyday spending = {total}. Unrecorded costs remain unknown. | English fallback; review needed | English fallback; review needed |
| explainUnknownCash | Available cash is unknown. The gap calculation assumes R0; recorded net income and savings contributions are not an available balance. | English fallback; review needed | English fallback; review needed |
| explainGapMath | Horizon gap: {costs} costs minus {income} estimated income minus {cash} assumed cash = {gap}, with negative results shown as zero. This does not establish when money will arrive or bills can be paid. | English fallback; review needed | English fallback; review needed |
| explainWeeklyMath | Weekly amount: {total} gap divided by {days} days, multiplied by 7 and rounded up to cents = {weekly}. This is a planning pace, not money already saved or proof it is affordable. | English fallback; review needed | English fallback; review needed |
| explainOverlap | A recommendation is unavailable because upcoming costs may overlap the everyday spending estimate. Check which costs are already covered before relying on the combined total. | English fallback; review needed | English fallback; review needed |
| explainIncomeHistory | A set-aside recommendation needs at least six completed weeks of recorded income history. Keep recording payouts and check that missing weeks are complete. | English fallback; review needed | English fallback; review needed |
| explainCostHistory | A recommendation needs dated upcoming costs or spending records spanning at least 14 recent calendar days. Add the bills you know about; a past recurring flag does not create a due date. | English fallback; review needed | English fallback; review needed |
| explainPlanningGap | Estimated costs exceed estimated income and assumed cash over this horizon. The difference is a conditional planning gap, not a predicted shortfall date. | English fallback; review needed | English fallback; review needed |
| explainNoGap | These inputs show no gap over the whole horizon. This does not establish that every bill can be paid on time; check upcoming dates and available cash. | English fallback; review needed | English fallback; review needed |
| explainUnavailable | A recommendation is unavailable from these inputs. Check your recorded income, upcoming costs and available cash. | English fallback; review needed | English fallback; review needed |
| editNamedEntry | Edit {label}, {amount}, {date} | English fallback; review needed | English fallback; review needed |
| deleteNamedEntry | Delete {label}, {amount}, {date} | English fallback; review needed | English fallback; review needed |
| confirmDelete | Delete {label}, {amount}, dated {date}? This cannot be undone. | English fallback; review needed | English fallback; review needed |
| entryCorrected | Entry corrected. | English fallback; review needed | English fallback; review needed |
| entryDeleted | Entry deleted. | English fallback; review needed | English fallback; review needed |
| entryChangeFailed | Could not change the entry. Your existing record is unchanged. Check your connection and try again. | English fallback; review needed | English fallback; review needed |
| sampleRecommendation | Fictional reference estimate | English fallback; review needed | English fallback; review needed |
| sampleReference | Sample recommendation, unchanged by preview edits | English fallback; review needed | English fallback; review needed |
| sampleForecastStatic | This fictional recommendation does not recalculate when you add, edit or delete preview entries. Only recorded totals change. It is not a recommendation for your finances. | English fallback; review needed | English fallback; review needed |
| planningEstimate | A conditional planning estimate | English fallback; review needed | English fallback; review needed |
| conditionalGap | Check this planning gap. | English fallback; review needed | English fallback; review needed |
| checkInputs | Check your upcoming costs and cash. | English fallback; review needed | English fallback; review needed |
| cashAssumption | Available cash is unknown. This planning estimate assumes no cash is available. Recorded net income is not your bank balance. | English fallback; review needed | English fallback; review needed |
| forecastMethod | The income estimate uses {weeks} completed weeks (up to eight), including weeks with no recorded earnings. Spending records span {days} days. At least two completed weeks are needed for an income estimate, and six plus an expense basis for a planning gap. | English fallback; review needed | English fallback; review needed |
| recurringAssumption | Enter upcoming bills with their due dates. A recurring checkbox alone does not establish a repeat date; past recurring bills are not automatically repeated. | English fallback; review needed | English fallback; review needed |
| forecastTiming | Weekly earnings do not tell us when your next payout will arrive. No exact shortfall date or probability is predicted. | English fallback; review needed | English fallback; review needed |
| incompleteHistory | Missing entries can change this estimate. Confidence has not been validated. | English fallback; review needed | English fallback; review needed |
| notEstablished | Not established | English fallback; review needed | English fallback; review needed |
| unvalidated | Unvalidated | English fallback; review needed | English fallback; review needed |
| conditionalSuggestion | A conditional allocation, not proof that money is available to save. | English fallback; review needed | English fallback; review needed |
| recordedThisMonth | Recorded set-asides this month | English fallback; review needed | English fallback; review needed |
| savingsNotCash | These records track money you put aside. They are not a verified savings balance or progress against a dated goal. | English fallback; review needed | English fallback; review needed |
| chartAssumption | Seven-day planning blocks; the final block may be shorter. No calibrated confidence range is shown for account estimates. | English fallback; review needed | English fallback; review needed |
| exportScope | This download contains only entries currently loaded in the app, not a complete account export. Keep it private on shared devices. Sample exports are marked fictional. | English fallback; review needed | English fallback; review needed |
| deleteAccountDecision | Self-service account deletion is not available yet. Before launch, the team must define identity verification, deletion of stored records, backup retention and a published contact route. Removing entries or signing out does not delete your account. | English fallback; review needed | English fallback; review needed |
| translationReview | Language draft: some text is shown in English. isiZulu and Sesotho wording, including financial terms and confirmations, needs fluent-speaker review. | English fallback; review needed | English fallback; review needed |
| bolokaHome | Boloka home | English fallback; review needed | English fallback; review needed |
| boloka | boloka | English fallback; review needed | English fallback; review needed |
| weCouldNotLoadYourMoneyPictureTry | We could not load your money picture. Try again. | English fallback; review needed | English fallback; review needed |
| weCouldNotCheckYourAccountCheckYour | We could not check your account. Check your connection and reload. | English fallback; review needed | English fallback; review needed |
| addEntriesToSeeASetAsideSuggestion | Add entries to see a set-aside suggestion. | English fallback; review needed | English fallback; review needed |
| addIncomeAndExpenseEntriesToBuildYour | Add income and expense entries to build your estimate. | English fallback; review needed | English fallback; review needed |
| income | Income | English fallback; review needed | English fallback; review needed |
| expense | Expense | English fallback; review needed | English fallback; review needed |
| checkYourInboxToConfirmYourEmailThen | Check your inbox to confirm your email, then sign in. | English fallback; review needed | English fallback; review needed |
| youReSignedInYourPrivateMoneyPicture | You’re signed in. Your private money picture is ready. | English fallback; review needed | English fallback; review needed |
| weCouldNotReachSignInCheckYour | We could not reach sign-in. Check your connection and try again. | English fallback; review needed | English fallback; review needed |
| youHaveBeenSignedOut | You have been signed out. | English fallback; review needed | English fallback; review needed |
| enterAnAmountGreaterThanR000 | Enter an amount greater than R0.00. | English fallback; review needed | English fallback; review needed |
| youAreOfflineReconnectBeforeSavingToYour | You are offline. Reconnect before saving to your account. | English fallback; review needed | English fallback; review needed |
| entrySavedToYourAccount | Entry saved to your account. | English fallback; review needed | English fallback; review needed |
| addedToThisSamplePreviewOnlySignIn | Added to this sample preview only. Sign in to save entries to your account. | English fallback; review needed | English fallback; review needed |
| couldNotSaveThisEntryTryAgain | Could not save this entry. Try again. | English fallback; review needed | English fallback; review needed |
| youAreOfflineReconnectBeforeSavingThisContribution | You are offline. Reconnect before saving this contribution. | English fallback; review needed | English fallback; review needed |
| yourSetAsideWasAddedToThisMonth | Your set-aside was added to this month’s buffer progress. | English fallback; review needed | English fallback; review needed |
| addedToThisSamplePreviewOnlySignIn2 | Added to this sample preview only. Sign in to keep the contribution in your account. | English fallback; review needed | English fallback; review needed |
| couldNotSaveThatSetAsideTryAgain | Could not save that set-aside. Try again. | English fallback; review needed | English fallback; review needed |
| youAreOfflineReconnectBeforeRemovingThisContribution | You are offline. Reconnect before removing this contribution. | English fallback; review needed | English fallback; review needed |
| setAsideRemoved | Set-aside removed. | English fallback; review needed | English fallback; review needed |
| couldNotRemoveThatSetAsideTryAgain | Could not remove that set-aside. Try again. | English fallback; review needed | English fallback; review needed |
| signInAndChooseACsvFileTo | Sign in and choose a CSV file to import income. | English fallback; review needed | English fallback; review needed |
| chooseACsvFileSmallerThan2Mb | Choose a CSV file smaller than 2 MB. | English fallback; review needed | English fallback; review needed |
| youAreOfflineReconnectBeforeImportingToYour | You are offline. Reconnect before importing to your account. | English fallback; review needed | English fallback; review needed |
| imported | Imported  | English fallback; review needed | English fallback; review needed |
| couldNotImportThatFile | Could not import that file. | English fallback; review needed | English fallback; review needed |
| skipToMainContent | Skip to main content | English fallback; review needed | English fallback; review needed |
| gettingYourMoneyPictureReady | Getting your money picture ready. | English fallback; review needed | English fallback; review needed |
| checkingYourAccountSecurely | Checking your account securely… | English fallback; review needed | English fallback; review needed |
| openAccountSettings | Open account settings | English fallback; review needed | English fallback; review needed |
| signInToYourAccount | Sign in to your account | English fallback; review needed | English fallback; review needed |
| loadingDashboard | Loading dashboard | English fallback; review needed | English fallback; review needed |
| loadingYourMoneyPicture | Loading your money picture… | English fallback; review needed | English fallback; review needed |
| weCouldnTRefreshYourAccountData | We couldn’t refresh your account data. | English fallback; review needed | English fallback; review needed |
| dismissMessage | Dismiss message | English fallback; review needed | English fallback; review needed |
| updatingYourMoneyPicture | Updating your money picture… | English fallback; review needed | English fallback; review needed |
| addIncomeOrABillToGetA | Add income or a bill to get a picture that’s yours. | English fallback; review needed | English fallback; review needed |
| giveYourNextWeekAHeadStart | Give your next week a head start. | English fallback; review needed | English fallback; review needed |
| setAsideALittleWhenAPayoutLands | Set aside a little when a payout lands. It can make a slower week feel less sudden. | English fallback; review needed | English fallback; review needed |
| seeYourBuffer | See your buffer | English fallback; review needed | English fallback; review needed |
| useRandsAndCentsForExample15000 | Use rands and cents, for example 150.00 | English fallback; review needed | English fallback; review needed |
| deliveryShiftMarketOrder | Delivery shift, market order… | English fallback; review needed | English fallback; review needed |
| transportRent | Transport, rent… | English fallback; review needed | English fallback; review needed |
| forExampleRentOrAMonthlyPhoneBill | For example, rent or a monthly phone bill | English fallback; review needed | English fallback; review needed |
| yourEntriesStayPrivateToYourAccountPreview | Your entries stay private to your account. Preview entries are not uploaded. | English fallback; review needed | English fallback; review needed |
| importIncomeFromACsv | Import income from a CSV | English fallback; review needed | English fallback; review needed |
| useColumns | Use columns | English fallback; review needed | English fallback; review needed |
| source | source | English fallback; review needed | English fallback; review needed |
| and | , and | English fallback; review needed | English fallback; review needed |
| receivedOn | received_on | English fallback; review needed | English fallback; review needed |
| datesMustUseYyyyMmDd | . Dates must use YYYY-MM-DD. | English fallback; review needed | English fallback; review needed |
| signInToImportEntriesToYourAccount | Sign in to import entries to your account. | English fallback; review needed | English fallback; review needed |
| aWeekCouldHelpBuildABuffer | a week could help build a buffer. | English fallback; review needed | English fallback; review needed |
| thisIsAnEstimateFromTheEntriesYou | This is an estimate from the entries you’ve recorded. It is not financial advice and cannot guarantee what you’ll earn or spend. | English fallback; review needed | English fallback; review needed |
| loadingForecastChart | Loading forecast chart… | English fallback; review needed | English fallback; review needed |
| addIncomeEntriesToCreateAWeeklyOutlook | Add income entries to create a weekly outlook. | English fallback; review needed | English fallback; review needed |
| weeklyForecastValues | Weekly forecast values | English fallback; review needed | English fallback; review needed |
| aSmallCushionBuiltAtYourPace | A small cushion, built at your pace. | English fallback; review needed | English fallback; review needed |
| bufferEmergencyFund | Buffer, emergency fund… | English fallback; review needed | English fallback; review needed |
| removeSetAside | Remove set-aside  | English fallback; review needed | English fallback; review needed |
| noSetAsidesRecordedYetYouCanStart | No set-asides recorded yet. You can start with any amount that feels manageable. | English fallback; review needed | English fallback; review needed |
| useSmallerTextOnlyForecastVisualsAndAsk | Use smaller text-only forecast visuals and ask the API to reduce transfer when supported. | English fallback; review needed | English fallback; review needed |
| createAnAccountToSaveYourEntriesPrivately | Create an account to save your entries privately. | English fallback; review needed | English fallback; review needed |
| signInToSeeYourPrivateDashboard | Sign in to see your private dashboard. | English fallback; review needed | English fallback; review needed |
| alreadyHaveAnAccountSignIn | Already have an account? Sign in | English fallback; review needed | English fallback; review needed |
| newToBolokaCreateAnAccount | New to Boloka? Create an account | English fallback; review needed | English fallback; review needed |
| accountSignInWillBeAvailableWhenThe | Account sign-in will be available when the team connects the Supabase project. | English fallback; review needed | English fallback; review needed |
| bolokaNeverAsksForYourBankPasswordYour | Boloka never asks for your bank password. Your entries are protected by account sign-in and row-level security. | English fallback; review needed | English fallback; review needed |
| week | Week  | English fallback; review needed | English fallback; review needed |
| importResult | Imported {imported} entries. {skipped} rows were skipped. | English fallback; review needed | English fallback; review needed |
| removeContributionLabel | Remove set-aside {amount}, dated {date} | English fallback; review needed | English fallback; review needed |
| cashScenarioHelp | Enter money you can use for these costs. This value is not bank verified, saved or included in exports. | English fallback; review needed | English fallback; review needed |
| cashScenarioUsed | This planning estimate uses the available cash you entered: {amount}. | English fallback; review needed | English fallback; review needed |
| csvInstructions | Use CSV columns amount, source, received_on and optional note. Dates use YYYY-MM-DD. | English fallback; review needed | English fallback; review needed |
| signInFailed | Sign-in could not be completed. Check the email, password and confirmation status, then try again. | English fallback; review needed | English fallback; review needed |
| loadFailed | Could not refresh account records. Check your connection and try again. | English fallback; review needed | English fallback; review needed |
| saveFailed | Could not save the record. Check the fields and your connection, then try again. | English fallback; review needed | English fallback; review needed |
| savedReloadFailed | Saved, but the updated records could not be reloaded. Use Try again to refresh; do not submit the same record twice. | English fallback; review needed | English fallback; review needed |
| signOutFailed | Could not sign out. Check your connection and try again. | English fallback; review needed | English fallback; review needed |
| planningIntro | Record your earnings and upcoming costs. Inspect a planning estimate, the history it uses and the assumptions behind it. | English fallback; review needed | English fallback; review needed |
| spendingAssumption | Everyday spending is estimated only when recent records span at least 14 days. Otherwise this total includes only explicit upcoming entries; other costs remain unknown. | English fallback; review needed | English fallback; review needed |
| spendingOverlap | Some upcoming costs may already be included in the everyday spending estimate. The combined total is a conservative scenario. No gap or set-aside recommendation is available until these costs can be distinguished. | English fallback; review needed | English fallback; review needed |
| csvImportLimits | Use UTF-8, at most 2 MB and 10,000 rows. Amounts use a dot and at most two decimal places. Reimporting a file adds duplicates; review existing entries first. | English fallback; review needed | English fallback; review needed |
| csvErrors | First skipped-row errors (English diagnostics) | English fallback; review needed | English fallback; review needed |
| csvRowError | Line {line}: {message} | English fallback; review needed | English fallback; review needed |

## Existing translated keys

Ticket #22 also adds `startNextSteps`, `startRecordIncome`, `startAddCosts`,
`startReviewCosts`, `startCheckCash`. Both isiZulu and Sesotho deliberately use
English fallback pending fluent review, especially the distinction between
missing entries, actual zero-income weeks and available cash.

Ticket #20 adds English fallback keys requiring fluent isiZulu/Sesotho review:
`explainCalculation`, `explainHorizon`, `explainIncomeMath`, `explainUnknownIncome`,
`explainCostsMath`, `explainUnknownCash`, `explainGapMath`, `explainWeeklyMath`,
`explainOverlap`, `explainIncomeHistory`, `explainCostHistory`, `explainPlanningGap`,
`explainNoGap`, `explainUnavailable`. Review the distinction between recorded
income, estimated earnings, assumed cash, an aggregate gap and affordability.
Preserve named placeholders and the meaning of rounding; do not imply timing or
validated accuracy. No new translation has been guessed or approved.

All existing translated keys require review too, particularly onboarding, privacy claims, recurring costs and scam warnings. Their presence is not evidence of language quality. Do not mark issue #28 complete until fluent reviewers approve the financial and destructive-action flows.
