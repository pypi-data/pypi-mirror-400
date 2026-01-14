import { Outlet, Link, useLocation } from 'react-router-dom'
import { useIntlayer, useLocale, LOCALE_INFO } from '@/providers'
import {
  LayoutDashboard,
  Database,
  Moon,
  Sun,
  Menu,
  GitCompare,
  Clock,
  Bell,
  Globe,
  Check,
  BookOpen,
  FolderOpen,
  Activity,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useTheme } from '@/components/theme-provider'
import { useState } from 'react'
import logoImg from '@/assets/logo.png'

type NavKey = 'dashboard' | 'sources' | 'catalog' | 'glossary' | 'drift' | 'schedules' | 'activity' | 'notifications'

const navigation: Array<{ key: NavKey; href: string; icon: typeof LayoutDashboard }> = [
  { key: 'dashboard', href: '/', icon: LayoutDashboard },
  { key: 'sources', href: '/sources', icon: Database },
  { key: 'catalog', href: '/catalog', icon: FolderOpen },
  { key: 'glossary', href: '/glossary', icon: BookOpen },
  { key: 'drift', href: '/drift', icon: GitCompare },
  { key: 'schedules', href: '/schedules', icon: Clock },
  { key: 'activity', href: '/activity', icon: Activity },
  { key: 'notifications', href: '/notifications', icon: Bell },
]

export default function Layout() {
  const location = useLocation()
  const nav = useIntlayer('nav')
  const { locale, setLocale } = useLocale()
  const { theme, setTheme } = useTheme()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const currentLang = LOCALE_INFO.find((l) => l.code === locale)

  return (
    <div className="min-h-screen bg-background" style={{ paddingTop: 'var(--demo-banner-height, 0px)' }}>
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          style={{ top: 'var(--demo-banner-height, 0px)' }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 bottom-0 z-50 w-48 transform bg-card border-r transition-transform duration-200 lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
        style={{ top: 'var(--demo-banner-height, 0px)' }}
      >
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b px-6">
          <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
            <img src={logoImg} alt="Truthound" className="h-6 w-6" />
          </div>
          <span className="font-semibold text-lg">Truthound</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          {navigation.map((item) => {
            const isActive =
              item.href === '/'
                ? location.pathname === '/'
                : location.pathname.startsWith(item.href)
            return (
              <Link
                key={item.key}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
              >
                <item.icon className="h-5 w-5" />
                {nav[item.key]}
              </Link>
            )
          })}
        </nav>

      </aside>

      {/* Main content */}
      <div className="lg:pl-48">
        {/* Top bar */}
        <header
          className="sticky z-30 flex h-16 items-center gap-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-6"
          style={{ top: 'var(--demo-banner-height, 0px)' }}
        >
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex-1" />
          <div className="flex items-center gap-1">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  title={currentLang?.nativeName}
                >
                  <Globe className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {LOCALE_INFO.map((lang) => (
                  <DropdownMenuItem
                    key={lang.code}
                    onClick={() => setLocale(lang.code)}
                    className="flex items-center justify-between gap-2"
                  >
                    <span>{lang.nativeName}</span>
                    {locale === lang.code && (
                      <Check className="h-4 w-4 text-primary" />
                    )}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              title="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
