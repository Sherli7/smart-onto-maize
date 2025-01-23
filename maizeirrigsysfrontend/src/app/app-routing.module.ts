import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { SensorsComponent } from './pages/sensors/sensors.component';
import { IrrigationComponent } from './pages/irrigation/irrigation.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'sensors', component: SensorsComponent },
  { path: 'irrigation', component: IrrigationComponent },
  { path: '**', redirectTo: '' }  // Redirection vers l'accueil si la route est invalide
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
