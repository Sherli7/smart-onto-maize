import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MaterialModule } from './material.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { HomeComponent } from './pages/home/home.component';
import { IrrigationComponent } from './pages/irrigation/irrigation.component';
import { SensorsComponent } from './pages/sensors/sensors.component';
import { HttpClient, HttpClientModule, provideHttpClient } from '@angular/common/http';


// Module principal
@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    IrrigationComponent,
    SensorsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    DragDropModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule,
    MaterialModule,
  ],
  providers: [
    provideHttpClient()
  ],
  bootstrap: [AppComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA], // Facultatif, utilisez-le uniquement si nécessaire
})
export class AppModule {}
