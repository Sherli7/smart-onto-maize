import { Component, computed, signal } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'maizeirrigsysfrontend';

  constructor(private router:Router) {}
  
}
