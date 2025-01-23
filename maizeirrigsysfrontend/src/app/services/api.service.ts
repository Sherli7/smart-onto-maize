import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Field } from '../models/fields';
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;  // Adresse de l'API Flask

  constructor(private http: HttpClient) {}

  getFields(): Observable<Field[]> {
    return this.http.get<Field[]>(`${this.apiUrl}/fields`);
  }

  startIrrigation(): Observable<any> {
    return this.http.post(`${this.apiUrl}/irrigation/start`, {});
  }
 
  getSensorData(): Observable<any> {
    return this.http.get(`${this.apiUrl}/sensors`);
  }

  stopIrrigation(): Observable<any> {
    return this.http.post(`${this.apiUrl}/irrigation/stop`, {});
  }

  getFieldDetails(id: number): Observable<Field> {
    return this.http.get<Field>(`${this.apiUrl}/fields/${id}`);
  }
}
