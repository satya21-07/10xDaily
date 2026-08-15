import { Routes } from '@angular/router';
import { TabsLayoutComponent } from './layout/tabs-layout/tabs-layout.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    component: TabsLayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'home',
        loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent)
      },
      {
        path: 'quiz',
        loadComponent: () => import('./features/quiz/quiz.component').then(m => m.QuizComponent)
      },
      {
        path: 'bookmarks',
        loadComponent: () => import('./features/bookmarks/bookmarks.component').then(m => m.BookmarksComponent)
      },
      {
        path: 'profile',
        loadComponent: () => import('./features/profile/profile.component').then(m => m.ProfileComponent)
      },
      {
        path: 'profile/personal-information',
        loadComponent: () => import('./features/profile/personal-information/personal-information.component').then(m => m.PersonalInformationComponent)
      },
      {
        path: 'profile/privacy-security',
        loadComponent: () => import('./features/profile/privacy-security/privacy-security.component').then(m => m.PrivacySecurityComponent)
      },
      {
        path: 'profile/help-support',
        loadComponent: () => import('./features/profile/help-support/help-support.component').then(m => m.HelpSupportComponent)
      },
      {
        path: 'games',
        loadComponent: () => import('./features/games/games-hub/games-hub.component').then(m => m.GamesHubComponent)
      },
      {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full'
      }
    ]
  },
  {
    path: 'games/flow',
    canActivate: [authGuard],
    loadComponent: () => import('./features/games/flow-puzzle/flow-puzzle.component').then(m => m.FlowPuzzleComponent)
  },
  {
    path: 'games/word-search',
    canActivate: [authGuard],
    loadComponent: () => import('./features/games/word-search/word-search.component').then(m => m.WordSearchComponent)
  },
  {
    path: 'games/mini-sudoku',
    canActivate: [authGuard],
    loadComponent: () => import('./features/games/mini-sudoku/mini-sudoku.component').then(m => m.MiniSudokuComponent)
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'vocabulary',
    canActivate: [authGuard],
    loadComponent: () => import('./features/vocabulary/vocabulary.component').then(m => m.VocabularyComponent)
  },
  {
    path: 'news',
    canActivate: [authGuard],
    loadComponent: () => import('./features/news/news.component').then(m => m.NewsComponent)
  },
  {
    path: 'coding',
    canActivate: [authGuard],
    loadComponent: () => import('./features/coding/coding.component').then(m => m.CodingComponent)
  },
  {
    path: 'finance',
    canActivate: [authGuard],
    loadComponent: () => import('./features/finance/finance.component').then(m => m.FinanceComponent)
  },
  {
    path: 'health',
    canActivate: [authGuard],
    loadComponent: () => import('./features/health/health.component').then(m => m.HealthComponent)
  },
  {
    path: 'spiritual',
    canActivate: [authGuard],
    loadComponent: () => import('./features/spiritual/spiritual.component').then(m => m.SpiritualComponent)
  }
];
