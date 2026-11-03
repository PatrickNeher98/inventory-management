<template>
  <div class="restocking">
    <div class="page-header">
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">{{ t('restocking.budget') }}</h3>
        <span class="budget-value">{{ displayMoney(budget) }}</span>
      </div>
      <input
        v-model.number="budget"
        type="range"
        class="budget-slider"
        :min="MIN_BUDGET"
        :max="MAX_BUDGET"
        :step="STEP"
        :aria-label="t('restocking.budget')"
      />
      <div class="slider-scale">
        <span>{{ displayMoney(MIN_BUDGET) }}</span>
        <span>{{ displayMoney(MAX_BUDGET) }}</span>
      </div>
    </div>

    <div v-if="confirmation" class="confirmation">{{ confirmation }}</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="stats-grid">
      <div class="stat-card info">
        <div class="stat-label">{{ t('restocking.selectedItems') }}</div>
        <div class="stat-value">{{ selectedItems.length }}</div>
      </div>
      <div :class="['stat-card', overBudget ? 'danger' : 'success']">
        <div class="stat-label">{{ t('restocking.totalCost') }}</div>
        <div class="stat-value">{{ displayMoney(selectedTotal) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
        <div class="stat-value">{{ displayMoney(budget - selectedTotal) }}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">{{ t('restocking.recommendations') }}</h3>
        <div class="actions">
          <span v-if="overBudget" class="over-budget">{{ t('restocking.overBudget') }}</span>
          <button class="place-btn" :disabled="!canPlace" @click="placeOrder">
            {{ placing ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>
      </div>

      <div v-if="loading && rows.length === 0" class="loading">{{ t('common.loading') }}</div>
      <div v-else-if="rows.length === 0 && !loading" class="loading">{{ t('restocking.noRecommendations') }}</div>
      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>{{ t('restocking.table.select') }}</th>
              <th>{{ t('restocking.table.sku') }}</th>
              <th>{{ t('restocking.table.name') }}</th>
              <th>{{ t('restocking.table.trend') }}</th>
              <th>{{ t('restocking.table.shortfall') }}</th>
              <th>{{ t('restocking.table.quantity') }}</th>
              <th>{{ t('restocking.table.unitCost') }}</th>
              <th>{{ t('restocking.table.lineTotal') }}</th>
              <th>{{ t('restocking.table.leadTime') }}</th>
              <th>{{ t('restocking.table.supplier') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.sku" :class="{ invalid: !validQty(row) }">
              <td><input v-model="row.selected" type="checkbox" :aria-label="row.sku" /></td>
              <td><strong>{{ row.sku }}</strong></td>
              <td>{{ translateProductName(row.name) }}</td>
              <td>
                <span :class="['badge', row.trend]">{{ t(`trends.${row.trend}`) }}</span>
              </td>
              <td>{{ row.shortfall }}</td>
              <td>
                <input
                  v-model.number="row.quantity"
                  type="number"
                  min="1"
                  max="1000000"
                  step="1"
                  class="qty-input"
                  :aria-label="t('restocking.table.quantity')"
                />
                <div v-if="!validQty(row)" class="row-error">{{ t('restocking.invalidRow') }}</div>
              </td>
              <td>{{ displayMoney(row.unit_cost, 2) }}</td>
              <td><strong>{{ displayMoney(lineTotal(row), 2) }}</strong></td>
              <td>{{ formatDays(row.lead_time_days) }}</td>
              <td>{{ row.supplier }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

const MIN_BUDGET = 0
const MAX_BUDGET = 500000
const STEP = 5000
const DEFAULT_BUDGET = 100000

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()

    const budget = ref(DEFAULT_BUDGET)
    const rows = ref([])
    const loading = ref(true)
    const placing = ref(false)
    const error = ref(null)
    const confirmation = ref(null)
    let debounceTimer = null
    let requestId = 0

    const displayMoney = (usd, decimals = 0) => {
      const value = Number(usd) || 0
      return decimals > 0
        ? formatCurrencyWithDecimals(value, currentCurrency.value, decimals)
        : formatCurrency(value, currentCurrency.value)
    }

    const validQty = (row) => Number.isInteger(row.quantity) && row.quantity > 0 && row.quantity <= 1000000
    const formatDays = (n) => t(n === 1 ? 'orders.day' : 'orders.days', { count: n })
    const lineTotal = (row) => (validQty(row) ? row.quantity * row.unit_cost : 0)

    const selectedItems = computed(() => rows.value.filter(r => r.selected && validQty(r)))
    const selectedTotal = computed(() =>
      selectedItems.value.reduce((sum, r) => sum + lineTotal(r), 0)
    )
    const overBudget = computed(() => selectedTotal.value > budget.value + 1e-9)
    const canPlace = computed(() =>
      selectedItems.value.length > 0 && !overBudget.value && !placing.value
    )

    const loadRecommendations = async () => {
      const id = ++requestId
      try {
        loading.value = true
        error.value = null
        const data = await api.getRestockRecommendations(budget.value)
        if (id !== requestId) return
        rows.value = data.items.map(item => ({ ...item, selected: true }))
      } catch (err) {
        if (id !== requestId) return
        error.value = t('restocking.loadError')
        console.error('Load error:', err)
      } finally {
        if (id === requestId) loading.value = false
      }
    }

    watch(budget, () => {
      confirmation.value = null
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(loadRecommendations, 300)
    })

    const placeOrder = async () => {
      if (!canPlace.value) return
      confirmation.value = null
      try {
        placing.value = true
        error.value = null
        confirmation.value = null
        const order = await api.createRestockOrder({
          budget: budget.value,
          items: selectedItems.value.map(r => ({
            sku: r.sku,
            name: r.name,
            quantity: r.quantity,
            unit_cost: r.unit_cost
          }))
        })
        confirmation.value = t('restocking.orderPlaced', {
          orderNumber: order.order_number,
          days: order.lead_time_days
        })
        await loadRecommendations()
      } catch (err) {
        error.value = t('restocking.orderError')
        console.error('Order error:', err)
      } finally {
        placing.value = false
      }
    }

    onMounted(loadRecommendations)
    onBeforeUnmount(() => clearTimeout(debounceTimer))

    return {
      t,
      MIN_BUDGET,
      MAX_BUDGET,
      STEP,
      budget,
      rows,
      loading,
      placing,
      error,
      confirmation,
      displayMoney,
      lineTotal,
      validQty,
      formatDays,
      selectedItems,
      selectedTotal,
      overBudget,
      canPlace,
      placeOrder,
      translateProductName
    }
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: var(--card-gap);
}

.stat-value {
  font-size: var(--text-xl);
  line-height: 1.3;
}

.stats-grid {
  margin-bottom: var(--card-gap);
}

.budget-value {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  color: var(--color-slate-900);
}

.budget-slider {
  width: 100%;
  accent-color: var(--color-accent);
}

.slider-scale {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-2);
  color: var(--color-slate-500);
  font-size: var(--text-sm);
}

.confirmation {
  background: var(--color-green-soft);
  border: 1px solid var(--color-green);
  color: #166534;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin-bottom: var(--card-gap);
  font-size: var(--text-base);
}

.error {
  margin: 0 0 var(--card-gap);
}

.actions {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.over-budget {
  color: var(--color-red);
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
}

.place-btn {
  background: var(--color-slate-900);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  font-family: inherit;
  cursor: pointer;
}

.place-btn:hover:not(:disabled) {
  background: var(--color-slate-700);
}

.place-btn:disabled {
  background: var(--color-slate-300);
  cursor: not-allowed;
}

.qty-input {
  width: 80px;
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--color-slate-200);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  font-family: inherit;
  color: var(--color-slate-700);
  text-align: right;
}

.row-error {
  color: var(--color-red);
  font-size: var(--text-xs);
  margin-top: var(--space-1);
}

tr.invalid {
  background: var(--color-red-soft);
}

.qty-input:invalid {
  border-color: var(--color-red);
}

th:nth-child(n+5):nth-child(-n+8),
td:nth-child(n+5):nth-child(-n+8) {
  text-align: right;
}
</style>
