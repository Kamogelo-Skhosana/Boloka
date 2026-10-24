export default function TransactionList({ items, amount, dateLabel, onEdit, onDelete, busy, tr }) {
  return <ul className="transaction-list">
    {items.map(item => <li className="transaction-row transaction-row--editable" key={item.kind + item.id}>
      <span className={'transaction-icon transaction-icon--' + item.kind} aria-hidden="true">{item.kind === 'income' ? '↑' : '↓'}</span>
      <span className="transaction-row__label"><strong>{item.label}</strong><small>{tr(item.kind === 'income' ? 'moneyIn' : 'moneyOut')} · {dateLabel(item.date)}</small></span>
      <span className={'transaction-row__amount transaction-row__amount--' + item.kind}>{item.kind === 'income' ? '+' : '−'}{amount(item.amount_cents)}</span>
      <span className="transaction-actions">
        <button id={'entry-edit-' + item.kind + item.id} className="text-button" type="button" disabled={busy} onClick={() => onEdit(item)} aria-label={tr('editNamedEntry', { label: item.label, amount: amount(item.amount_cents), date: dateLabel(item.date) })}>{tr('edit')}</button>
        <button className="text-button" type="button" disabled={busy} onClick={() => onDelete(item)} aria-label={tr('deleteNamedEntry', { label: item.label, amount: amount(item.amount_cents), date: dateLabel(item.date) })}>{tr('delete')}</button>
      </span>
    </li>)}
  </ul>
}
