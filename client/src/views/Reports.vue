<template>
  <div class="reports">
    <div class="page-header">
      <p>{{ t('reports.description') }}</p>
    </div>

    <div v-if="loading && quarterlyData.length === 0 && monthlyData.length === 0" class="loading">{{ t('reports.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="quarterlyData.length === 0 && monthlyData.length === 0" class="loading">{{ t('reports.noData') }}</div>
    <div v-else>
      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('reports.stats.totalRevenue') }}</div>
          <div class="stat-value">{{ money(totalRevenue) }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('reports.stats.avgMonthlyRevenue') }}</div>
          <div class="stat-value">{{ money(avgMonthlyRevenue) }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('reports.stats.totalOrders') }}</div>
          <div class="stat-value">{{ totalOrders }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('reports.stats.bestQuarter') }}</div>
          <div class="stat-value">{{ bestQuarter }}</div>
        </div>
      </div>

      <!-- Quarterly Performance -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.quarterly.title') }}</h3>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>{{ t('reports.quarterly.quarter') }}</th>
                <th>{{ t('reports.quarterly.totalOrders') }}</th>
                <th>{{ t('reports.quarterly.totalRevenue') }}</th>
                <th>{{ t('reports.quarterly.avgOrderValue') }}</th>
                <th>{{ t('reports.quarterly.fulfillmentRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="q in quarterlyData" :key="q.quarter">
                <td><strong>{{ q.quarter }}</strong></td>
                <td>{{ q.total_orders }}</td>
                <td>{{ money(q.total_revenue) }}</td>
                <td>{{ money(q.avg_order_value) }}</td>
                <td>
                  <span :class="getFulfillmentClass(q.fulfillment_rate)">
                    {{ q.fulfillment_rate }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Monthly Trends Chart -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.trend.title') }}</h3>
        </div>
        <div class="chart-container">
          <div class="bar-chart">
            <div v-for="month in monthlyData" :key="month.month" class="bar-wrapper">
              <div class="bar-container">
                <div
                  class="bar"
                  :style="{ height: getBarHeight(month.revenue) + 'px' }"
                  :title="money(month.revenue)"
                ></div>
              </div>
              <div class="bar-label">{{ formatMonth(month.month) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Month-over-Month Comparison -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.mom.title') }}</h3>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>{{ t('reports.mom.month') }}</th>
                <th>{{ t('reports.mom.orders') }}</th>
                <th>{{ t('reports.mom.revenue') }}</th>
                <th>{{ t('reports.mom.change') }}</th>
                <th>{{ t('reports.mom.growthRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="month in monthlyRows" :key="month.month">
                <td><strong>{{ formatMonth(month.month) }}</strong></td>
                <td>{{ month.order_count }}</td>
                <td>{{ money(month.revenue) }}</td>
                <td>
                  <span v-if="month.hasPrev" :class="month.changeClass">{{ month.changeText }}</span>
                  <span v-else>-</span>
                </td>
                <td>
                  <span v-if="month.hasPrev" :class="month.changeClass">{{ month.rateText }}</span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency } from '../utils/currency'

export default {
  name: 'Reports',
  setup() {
    const { t, currentLocale, currentCurrency } = useI18n()
    const { selectedPeriod, selectedLocation, selectedCategory, selectedStatus, getCurrentFilters } = useFilters()

    const loading = ref(true)
    const error = ref(null)
    const quarterlyData = ref([])
    const monthlyData = ref([])

    let requestId = 0
    const loadData = async () => {
      const current = ++requestId
      try {
        loading.value = true
        error.value = null
        const filters = getCurrentFilters()
        const [quarterly, monthly] = await Promise.all([
          api.getQuarterlyReports(filters),
          api.getMonthlyTrends(filters)
        ])
        if (current !== requestId) return
        quarterlyData.value = quarterly
        monthlyData.value = monthly
      } catch (err) {
        if (current !== requestId) return
        error.value = t('reports.loadError') + ': ' + err.message
        console.error('Reports load error:', err)
      } finally {
        if (current === requestId) loading.value = false
      }
    }

    watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], loadData)
    onMounted(loadData)

    const money = (amount) => formatCurrency(amount, currentCurrency.value)

    const totalRevenue = computed(() => monthlyData.value.reduce((sum, m) => sum + m.revenue, 0))
    const avgMonthlyRevenue = computed(() =>
      monthlyData.value.length > 0 ? totalRevenue.value / monthlyData.value.length : 0
    )
    const totalOrders = computed(() => monthlyData.value.reduce((sum, m) => sum + m.order_count, 0))
    const bestQuarter = computed(() => {
      let best = null
      for (const q of quarterlyData.value) {
        if (!best || q.total_revenue > best.total_revenue) best = q
      }
      return best ? best.quarter : '-'
    })
    const maxRevenue = computed(() => Math.max(0, ...monthlyData.value.map(m => m.revenue)))

    const formatMonth = (monthStr) => {
      const date = new Date(`${monthStr}-01T00:00:00`)
      if (isNaN(date.getTime())) return monthStr
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return date.toLocaleDateString(locale, { year: 'numeric', month: 'short' })
    }

    const getBarHeight = (revenue) => {
      if (maxRevenue.value === 0) return 0
      return (revenue / maxRevenue.value) * 200
    }

    const getFulfillmentClass = (rate) => {
      if (rate >= 90) return 'badge success'
      if (rate >= 75) return 'badge warning'
      return 'badge danger'
    }

    // Month-over-month rows with precomputed deltas
    const monthlyRows = computed(() =>
      monthlyData.value.map((m, i) => {
        if (i === 0) return { ...m, hasPrev: false }
        const prev = monthlyData.value[i - 1].revenue
        const change = m.revenue - prev
        const rate = prev === 0 ? null : (change / prev) * 100
        return {
          ...m,
          hasPrev: true,
          changeClass: change > 0 ? 'positive-change' : change < 0 ? 'negative-change' : '',
          changeText: (change > 0 ? '+' : change < 0 ? '-' : '') + money(Math.abs(change)),
          rateText: rate === null ? 'N/A' : (rate > 0 ? '+' : '') + rate.toFixed(1) + '%'
        }
      })
    )

    return {
      t, loading, error, quarterlyData, monthlyData, monthlyRows,
      totalRevenue, avgMonthlyRevenue, totalOrders, bestQuarter,
      money, formatMonth, getBarHeight, getFulfillmentClass
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  margin-bottom: var(--card-gap);
}

.reports-table th:nth-child(n+2),
.reports-table td:nth-child(n+2) {
  text-align: right;
}

.chart-container {
  padding: var(--space-6) var(--space-4) var(--space-8);
  min-height: 300px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  gap: var(--space-2);
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
}

.bar-container {
  height: 200px;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.bar {
  width: 100%;
  background: var(--color-blue);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: opacity 0.2s;
  cursor: pointer;
}

.bar:hover {
  opacity: 0.8;
}

.bar-label {
  font-size: var(--text-xs);
  color: var(--color-slate-500);
  text-align: center;
  transform: rotate(-45deg);
  white-space: nowrap;
  margin-top: var(--space-6);
}

.badge {
  border-radius: var(--radius-full);
  text-transform: none;
  letter-spacing: normal;
  font-weight: var(--weight-medium);
}

.positive-change {
  color: var(--color-green);
  font-weight: var(--weight-semibold);
}

.negative-change {
  color: var(--color-red);
  font-weight: var(--weight-semibold);
}
</style>
