import { translate } from '../lib/copy'
import { formatMoney } from '../lib/format'

const reasonKeys = {
  overlapping_costs: 'explainOverlap',
  insufficient_income_history: 'explainIncomeHistory',
  insufficient_cost_history: 'explainCostHistory',
  planning_gap: 'explainPlanningGap',
  no_gap_in_estimate: 'explainNoGap',
}

export default function ForecastExplanation({ forecast, language }) {
  const calculation = forecast?.calculation
  if (!calculation) return null
  const tr = (key, variables) => translate(language, key, variables)
  const money = cents => formatMoney(cents, language)
  return (
    <div>
      <p className="muted-note">{tr(reasonKeys[forecast.recommendation_reason] || 'explainUnavailable')}</p>
      <details className="import-details">
        <summary>{tr('explainCalculation')}</summary>
        <ul className="forecast-assumptions">
          <li>{tr('explainHorizon', { start: forecast.horizon_start, end: forecast.horizon_end })}</li>
          <li>{forecast.income_estimate_available
            ? tr('explainIncomeMath', { total: money(calculation.income_history_cents), historyDays: calculation.income_history_days, days: forecast.horizon_days, estimate: money(forecast.predicted_income_cents) })
            : tr('explainUnknownIncome')}</li>
          <li>{tr('explainCostsMath', { scheduled: money(forecast.scheduled_expenses_cents), everyday: money(forecast.everyday_expenses_cents), total: money(forecast.predicted_expenses_cents) })}</li>
          <li>{forecast.available_balance_cents == null
            ? tr('explainUnknownCash')
            : tr('cashScenarioUsed', { amount: money(calculation.cash_assumed_cents) })}</li>
          {forecast.shortfall?.status !== 'insufficient_data' ? <li>{tr('explainGapMath', { costs: money(forecast.predicted_expenses_cents), income: money(forecast.predicted_income_cents), cash: money(calculation.cash_assumed_cents), gap: money(forecast.shortfall.amount_cents) })}</li> : null}
          {forecast.shortfall?.status === 'planning_gap' ? <li>{tr('explainWeeklyMath', { total: money(forecast.set_aside.total_cents), days: forecast.horizon_days, weekly: money(forecast.set_aside.weekly_cents) })}</li> : null}
        </ul>
      </details>
    </div>
  )
}
