import { Area, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function ForecastChart({ series, formatAmount, formatDate, reducedMotion }) {
  const chartData = series.map((week, index) => {
    const value = week.predicted_income_cents ?? week.amount_cents ?? 0
    return {
      ...week,
      week_label: 'Week ' + (index + 1),
      range: [week.lower_cents ?? Math.round(value * 0.5), week.upper_cents ?? Math.round(value * 1.5)],
    }
  })

  return (
    <div className="recharts-wrap" role="group" aria-label={`Estimated income chart across ${series.length} weeks`}>
      <ResponsiveContainer width="100%" height={260}>
        <ComposedChart data={chartData} accessibilityLayer margin={{ top: 16, right: 16, left: 6, bottom: 8 }}>
          <CartesianGrid stroke="#33463d" strokeDasharray="4 5" vertical={false} />
          <XAxis dataKey="week_label" stroke="#b0c0b8" tickLine={false} axisLine={false} />
          <YAxis stroke="#b0c0b8" tickLine={false} axisLine={false} width={90} tickFormatter={formatAmount} />
          <Tooltip
            labelFormatter={(_label, items) => items?.[0]?.payload?.week_start ? formatDate(items[0].payload.week_start, { day: 'numeric', month: 'long' }) : ''}
            formatter={(value, name) => [Array.isArray(value) ? value.map(formatAmount).join(' – ') : formatAmount(value), name === 'predicted_income_cents' ? 'Estimated income' : 'Possible range']}
            contentStyle={{ border: '1px solid #53695e', borderRadius: '0.7rem', background: '#14221d', color: '#f3f7f4' }}
          />
          <Area type="monotone" dataKey="range" name="Possible range" stroke="#32d6a6" fill="#32d6a6" fillOpacity={0.15} isAnimationActive={!reducedMotion} />
          <Line type="monotone" dataKey="predicted_income_cents" name="Estimated income" stroke="#76f0c7" strokeWidth={3} dot={{ r: 4, fill: '#76f0c7' }} activeDot={{ r: 6 }} isAnimationActive={!reducedMotion} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
