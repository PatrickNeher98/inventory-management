<template>
  <div class="app-shell" :class="{ collapsed, 'drawer-open': drawerOpen }">
    <a class="skip-link" href="#main-content" @click.prevent="skipToContent">{{ t('nav.skipToContent') }}</a>
    <div class="sidebar-backdrop" aria-hidden="true" @click="closeDrawer()"></div>

    <aside id="app-sidebar" ref="sidebarRef" class="sidebar" :aria-label="t('nav.sidebar')" @keydown.tab="trapTab">
      <div class="sidebar-brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 8l-9-5-9 5 9 5 9-5z" />
            <path d="M3 8v8l9 5 9-5V8" />
          </svg>
        </span>
        <span class="brand-text">
          <span class="brand-name">{{ t('nav.companyName') }}</span>
          <span class="brand-subtitle">{{ t('nav.subtitle') }}</span>
        </span>
        <button
          type="button"
          class="drawer-close"
          :aria-label="t('nav.closeMenu')"
          @click="closeDrawer({ restoreFocus: true })"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" aria-hidden="true">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>

      <nav class="sidebar-nav" :aria-label="t('nav.main')">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :title="collapsed ? t(item.labelKey) : null"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path v-for="d in item.icon" :key="d" :d="d" />
          </svg>
          <span class="nav-label">{{ t(item.labelKey) }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
        <button
          type="button"
          class="collapse-toggle"
          :aria-label="collapsed ? t('nav.expand') : t('nav.collapse')"
          :title="collapsed ? t('nav.expand') : t('nav.collapse')"
          @click="toggleCollapsed"
        >
          <svg class="nav-icon collapse-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M3 4h18v16H3z" />
            <path d="M9 4v16" />
            <path d="M15 9l-3 3 3 3" />
          </svg>
          <span class="nav-label">{{ collapsed ? t('nav.expand') : t('nav.collapse') }}</span>
        </button>
      </div>
    </aside>

    <div class="app-main" :inert="drawerOpen && isMobile ? '' : null">
      <header class="topbar">
        <div class="topbar-row">
          <button
            ref="hamburgerRef"
            type="button"
            class="hamburger"
            :aria-label="t('nav.openMenu')"
            :aria-expanded="drawerOpen"
            aria-controls="app-sidebar"
            @click="toggleDrawer"
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" aria-hidden="true">
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 ref="titleRef" tabindex="-1" class="topbar-title">{{ pageTitle }}</h1>
        </div>
        <FilterBar />
      </header>
      <main id="main-content" ref="contentRef" class="content" tabindex="-1">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, nextTick, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()

    const COLLAPSE_KEY = 'sidebar-collapsed'
    const readCollapsed = () => {
      try {
        return localStorage.getItem(COLLAPSE_KEY) === 'true'
      } catch (e) {
        return false
      }
    }
    const collapsed = ref(readCollapsed())
    const drawerOpen = ref(false)
    const hamburgerRef = ref(null)
    const sidebarRef = ref(null)
    const titleRef = ref(null)
    const contentRef = ref(null)

    const mql = window.matchMedia('(max-width: 767px)')
    const isMobile = ref(mql.matches)

    // Nav items: route path -> i18n key (+ inline SVG icon paths)
    const navItems = [
      { path: '/', labelKey: 'nav.overview', icon: ['M3 3h7v9H3z', 'M14 3h7v5h-7z', 'M14 12h7v9h-7z', 'M3 16h7v5H3z'] },
      { path: '/inventory', labelKey: 'nav.inventory', icon: ['M21 8l-9-5-9 5 9 5 9-5z', 'M3 8v8l9 5 9-5V8', 'M12 13v8'] },
      { path: '/orders', labelKey: 'nav.orders', icon: ['M9 4h6v3H9z', 'M7 5.5H5a1 1 0 00-1 1V20a1 1 0 001 1h14a1 1 0 001-1V6.5a1 1 0 00-1-1h-2', 'M8 12h8', 'M8 16h5'] },
      { path: '/demand', labelKey: 'nav.demandForecast', icon: ['M3 17l6-6 4 4 8-8', 'M15 7h6v6'] },
      { path: '/spending', labelKey: 'nav.finance', icon: ['M12 3v18', 'M16.5 7.5C16 6 14.2 5 12 5c-2.5 0-4.5 1.2-4.5 3s1.8 2.6 4.5 3 4.5 1.2 4.5 3-2 3-4.5 3c-2.2 0-4-1-4.5-2.5'] },
      { path: '/restocking', labelKey: 'nav.restocking', icon: ['M20 11a8 8 0 00-14.9-3', 'M4 4v4h4', 'M4 13a8 8 0 0014.9 3', 'M20 20v-4h-4'] },
      { path: '/reports', labelKey: 'nav.reports', icon: ['M4 21V11', 'M10 21V4', 'M16 21v-7', 'M3 21h18'] }
    ]

    const pageTitle = computed(() => {
      const item = navItems.find(i => i.path === route.path)
      return item ? t(item.labelKey) : t('nav.companyName')
    })

    const toggleCollapsed = () => {
      collapsed.value = !collapsed.value
      try {
        localStorage.setItem(COLLAPSE_KEY, String(collapsed.value))
      } catch (e) {
        // storage unavailable; state stays in memory
      }
    }

    const showProfileDetails = ref(false)
    const showTasks = ref(false)

    const closeDrawer = ({ restoreFocus = false } = {}) => {
      if (!drawerOpen.value) return
      drawerOpen.value = false
      if (restoreFocus === true) {
        // app-main is inert until the DOM updates
        nextTick(() => hamburgerRef.value && hamburgerRef.value.focus())
      }
    }
    const openDrawer = async () => {
      drawerOpen.value = true
      await nextTick()
      const el = sidebarRef.value &&
        (sidebarRef.value.querySelector('.nav-link.router-link-exact-active') ||
         sidebarRef.value.querySelector('.nav-link'))
      if (el) el.focus()
    }
    const toggleDrawer = () => {
      if (drawerOpen.value) closeDrawer({ restoreFocus: true })
      else openDrawer()
    }
    const onKeydown = (e) => {
      if (e.key !== 'Escape' || e.defaultPrevented) return
      if (showTasks.value || showProfileDetails.value) return
      closeDrawer({ restoreFocus: true })
    }
    // Keep Tab inside the drawer while it is open on mobile
    const trapTab = (e) => {
      if (!(drawerOpen.value && isMobile.value) || !sidebarRef.value) return
      const items = [...sidebarRef.value.querySelectorAll('a[href], button:not([disabled])')]
        .filter(el => el.offsetParent !== null || el === document.activeElement)
      if (!items.length) return
      const first = items[0]
      const last = items[items.length - 1]
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
    const skipToContent = () => {
      if (contentRef.value) contentRef.value.focus()
    }
    const onMqChange = (e) => {
      isMobile.value = e.matches
      if (!e.matches) closeDrawer()
    }

    watch(pageTitle, (title) => {
      document.title = `${title} - ${t('nav.companyName')}`
    }, { immediate: true })
    watch(() => route.path, async () => {
      closeDrawer()
      await nextTick()
      if (contentRef.value) contentRef.value.scrollTo(0, 0)
      if (titleRef.value) titleRef.value.focus({ preventScroll: true })
    })
    onMounted(() => {
      window.addEventListener('keydown', onKeydown)
      mql.addEventListener('change', onMqChange)
    })
    onBeforeUnmount(() => {
      window.removeEventListener('keydown', onKeydown)
      mql.removeEventListener('change', onMqChange)
    })
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      navItems,
      pageTitle,
      collapsed,
      drawerOpen,
      hamburgerRef,
      sidebarRef,
      titleRef,
      contentRef,
      isMobile,
      trapTab,
      skipToContent,
      toggleCollapsed,
      toggleDrawer,
      closeDrawer,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
/* ==========================================================================
   Design tokens
   ========================================================================== */
:root {
  /* Spacing (4/8px grid) */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px; --space-12: 48px;

  /* Radius */
  --radius-sm: 6px; --radius-md: 8px; --radius-lg: 12px; --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.16);

  /* Slate palette */
  --color-slate-900: #0f172a;
  --color-slate-700: #334155;
  --color-slate-600: #475569;
  --color-slate-500: #64748b;
  --color-slate-300: #cbd5e1;
  --color-slate-200: #e2e8f0;
  --color-slate-100: #f1f5f9;
  --color-slate-50:  #f8fafc;
  --color-surface:   #ffffff;
  --color-accent:    #2563eb;
  --color-accent-soft: #eff6ff;

  /* Status */
  --color-green:  #16a34a; --color-green-soft:  #dcfce7;
  --color-blue:   #2563eb; --color-blue-soft:   #dbeafe;
  --color-yellow: #ca8a04; --color-yellow-soft: #fef9c3;
  --color-red:    #dc2626; --color-red-soft:    #fee2e2;

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans JP", sans-serif;
  --text-xs: 12px; --text-sm: 13px; --text-base: 14px;
  --text-md: 16px; --text-lg: 20px; --text-xl: 24px;
  --weight-regular: 400; --weight-medium: 500; --weight-semibold: 600;

  /* Card tokens (reuse in views via .card / .stat-card or these vars) */
  --card-bg: var(--color-surface);
  --card-border: 1px solid var(--color-slate-200);
  --card-radius: var(--radius-lg);
  --card-shadow: var(--shadow-sm);
  --card-shadow-hover: var(--shadow-md);
  --card-padding: var(--space-6);
  --card-gap: var(--space-4);

  /* Layout */
  --sidebar-width: 240px;
  --sidebar-width-collapsed: 72px;
  --topbar-height: 60px;
  --content-max-width: 1360px;

  /* Layers */
  --z-topbar: 20; --z-backdrop: 40; --z-sidebar: 50; --z-dropdown: 60;

  --color-backdrop: rgba(15, 23, 42, 0.4);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--color-slate-50);
  color: var(--color-slate-900);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* ==========================================================================
   App shell
   ========================================================================== */
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--color-slate-50);
}

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: var(--z-sidebar);
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: 1px solid var(--color-slate-200);
  color: var(--color-slate-700);
  transition: width 0.2s ease, transform 0.2s ease;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-height);
  padding: 0 var(--space-4);
  border-bottom: 1px solid var(--color-slate-200);
  flex-shrink: 0;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--color-slate-900);
  color: var(--color-surface);
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--color-slate-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-subtitle {
  font-size: var(--text-xs);
  color: var(--color-slate-500);
  line-height: 1.25;
  white-space: normal;
  overflow-wrap: anywhere;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-4) var(--space-3);
  overflow-y: auto;
}

.nav-link,
.collapse-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 40px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-slate-600);
  text-decoration: none;
  font-family: inherit;
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.nav-link:hover,
.collapse-toggle:hover {
  background: var(--color-slate-100);
  color: var(--color-slate-900);
}

.nav-link.router-link-exact-active {
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.nav-icon {
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  border-top: 1px solid var(--color-slate-200);
  flex-shrink: 0;
}

/* Restyle existing footer components (scoped styles live in each component) */
.sidebar .sidebar-footer .language-switcher,
.sidebar .sidebar-footer .profile-menu {
  width: 100%;
}

.sidebar .sidebar-footer .language-button,
.sidebar .sidebar-footer .profile-button {
  width: 100%;
  min-height: 40px;
  padding: var(--space-1) var(--space-3);
  background: var(--color-slate-50);
  border: 1px solid var(--color-slate-200);
  border-radius: var(--radius-md);
}

.sidebar .sidebar-footer .language-button:hover,
.sidebar .sidebar-footer .profile-button:hover {
  background: var(--color-slate-100);
}

.sidebar .sidebar-footer .chevron {
  margin-left: auto;
}

.sidebar .sidebar-footer .profile-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Dropdowns open upward and rightward from the footer */
.sidebar .sidebar-footer .dropdown-menu {
  top: auto;
  bottom: calc(100% + var(--space-2));
  left: 0;
  right: auto;
}

/* Menus open upward: closed chevron points up, open points down */
.sidebar .sidebar-footer .chevron {
  transform: rotate(180deg);
}

.sidebar .sidebar-footer .chevron.chevron-open {
  transform: rotate(0deg);
}

.sidebar .sidebar-footer .dropdown-menu {
  z-index: var(--z-dropdown);
}

.skip-link {
  position: absolute;
  left: var(--space-2);
  top: var(--space-2);
  z-index: calc(var(--z-dropdown) + 1);
  padding: var(--space-2) var(--space-3);
  background: var(--color-surface);
  color: var(--color-accent);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  transform: translateY(-200%);
}

.skip-link:focus {
  transform: none;
}

.drawer-close {
  display: none;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border: 1px solid var(--color-slate-200);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-slate-700);
  cursor: pointer;
}

.sidebar-backdrop {
  display: none;
}

.hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--color-slate-200);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-slate-700);
  cursor: pointer;
}

.hamburger:hover {
  background: var(--color-slate-100);
}

.app-main {
  flex: 1;
  min-width: 0;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  transition: margin-left 0.2s ease;
}

.topbar {
  position: relative;
  z-index: var(--z-topbar);
  flex-shrink: 0;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-slate-200);
}

.topbar-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-height);
  padding: 0 var(--space-6);
}

.topbar-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-slate-900);
  letter-spacing: -0.01em;
}

/* Embed the existing FilterBar inside the top bar (overrides its scoped sticky layout) */
.app-shell .topbar .filters-bar {
  position: static;
  background: var(--color-slate-50);
  border-top: 1px solid var(--color-slate-200);
  border-bottom: none;
  padding: var(--space-2) 0;
}

.app-shell .topbar .filters-container {
  max-width: none;
  margin: 0;
  padding: 0 var(--space-6);
}

.app-shell .topbar .filters-grid {
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.content > * {
  max-width: var(--content-max-width);
  margin-left: auto;
  margin-right: auto;
}

/* Desktop: icon rail */
@media (min-width: 768px) {
  .collapsed .sidebar {
    width: var(--sidebar-width-collapsed);
  }

  .collapsed .app-main {
    margin-left: var(--sidebar-width-collapsed);
  }

  .collapsed .sidebar-brand {
    justify-content: center;
    padding: 0;
  }

  .collapsed .brand-text,
  .collapsed .nav-label,
  .collapsed .sidebar .sidebar-footer .profile-name,
  .collapsed .sidebar .sidebar-footer .language-label,
  .collapsed .sidebar .sidebar-footer .chevron {
    position: absolute;
    width: 1px;
    height: 1px;
    margin: -1px;
    padding: 0;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .collapsed .nav-link,
  .collapsed .collapse-toggle,
  .collapsed .sidebar .sidebar-footer .language-button,
  .collapsed .sidebar .sidebar-footer .profile-button {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }

  .collapsed .collapse-icon {
    transform: scaleX(-1);
  }
}

/* Mobile: off-canvas drawer */
@media (max-width: 767px) {
  .sidebar {
    width: var(--sidebar-width);
    transform: translateX(-100%);
    visibility: hidden;
    transition: transform 0.2s ease, visibility 0s linear 0.2s;
  }

  .drawer-open .sidebar {
    transform: none;
    visibility: visible;
    box-shadow: var(--shadow-lg);
    transition: transform 0.2s ease, visibility 0s;
  }

  .drawer-open .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: var(--z-backdrop);
    background: var(--color-backdrop);
  }

  .app-main {
    margin-left: 0;
  }

  .hamburger {
    display: inline-flex;
  }

  .drawer-close {
    display: inline-flex;
  }

  .collapse-toggle {
    display: none;
  }

  .topbar-row {
    padding: 0 var(--space-4);
  }

  .app-shell .topbar .filters-container {
    padding: 0 var(--space-4);
  }

  .app-shell .topbar .filters-grid {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: var(--space-1);
  }

  .content {
    padding: var(--space-4);
  }
}

@media (prefers-reduced-motion: reduce) {
  .sidebar,
  .app-main,
  .nav-link,
  .collapse-toggle {
    transition: none;
  }
}

/* ==========================================================================
   Shared view styles (phase 2: views should use these classes)
   ========================================================================== */
.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-slate-900);
  margin-bottom: 0.375rem;
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--color-slate-500);
  font-size: 0.938rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--card-gap);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--card-bg);
  padding: var(--space-4) var(--space-6);
  border-radius: var(--card-radius);
  border: var(--card-border);
  box-shadow: var(--card-shadow);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.stat-card:hover {
  border-color: var(--color-slate-300);
  box-shadow: var(--card-shadow-hover);
}

.stat-label {
  color: var(--color-slate-500);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.625rem;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--color-slate-900);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: #ea580c;
}

.stat-card.success .stat-value {
  color: #059669;
}

.stat-card.danger .stat-value {
  color: var(--color-red);
}

.stat-card.info .stat-value {
  color: var(--color-blue);
}

.card {
  background: var(--card-bg);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  border: var(--card-border);
  box-shadow: var(--card-shadow);
  margin-bottom: var(--card-gap);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--color-slate-200);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-slate-900);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--color-slate-50);
  border-top: 1px solid var(--color-slate-200);
  border-bottom: 1px solid var(--color-slate-200);
}

th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  color: var(--color-slate-600);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 0.5rem 0.75rem;
  border-top: 1px solid var(--color-slate-100);
  color: var(--color-slate-700);
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--color-slate-50);
}

.badge {
  display: inline-block;
  padding: 0.313rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: #d1fae5;
  color: #065f46;
}

.badge.warning {
  background: #fed7aa;
  color: #92400e;
}

.badge.danger {
  background: #fecaca;
  color: #991b1b;
}

.badge.info {
  background: var(--color-blue-soft);
  color: #1e40af;
}

.badge.increasing {
  background: #d1fae5;
  color: #065f46;
}

.badge.decreasing {
  background: #fecaca;
  color: #991b1b;
}

.badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.badge.high {
  background: #fecaca;
  color: #991b1b;
}

.badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.badge.low {
  background: var(--color-blue-soft);
  color: #1e40af;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--color-slate-500);
  font-size: 0.938rem;
}

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 1rem;
  border-radius: var(--radius-md);
  margin: 1rem 0;
  font-size: 0.938rem;
}
</style>
