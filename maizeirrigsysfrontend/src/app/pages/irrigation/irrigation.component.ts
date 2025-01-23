import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-irrigation',
  templateUrl: './irrigation.component.html',
  styleUrls: ['./irrigation.component.scss']
})
export class IrrigationComponent {
  constructor(private apiService: ApiService) {}

  startIrrigation() {
    this.apiService.startIrrigation().subscribe(response => {
      alert(response.status);
    });
  }
}
