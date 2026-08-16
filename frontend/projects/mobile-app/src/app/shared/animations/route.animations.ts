import { trigger, transition, style, query, animate, group } from '@angular/animations';

export const routeTransitionAnimations = trigger('routeTransitionAnimations', [
  transition('* <=> *', [
    // Set up the entering and leaving elements to be absolute
    // so they overlap during the animation
    query(':enter, :leave', [
      style({
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%'
      })
    ], { optional: true }),
    
    // Set initial state of entering element to transparent
    query(':enter', [
      style({ opacity: 0 })
    ], { optional: true }),
    
    // Run entering and leaving animations in parallel
    group([
      query(':leave', [
        animate('300ms ease-out', style({ opacity: 0 }))
      ], { optional: true }),
      query(':enter', [
        animate('300ms ease-in', style({ opacity: 1 }))
      ], { optional: true })
    ])
  ])
]);
