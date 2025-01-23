import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Field } from '../../models/fields';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  fields: Field[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.apiService.getFields().subscribe(data => {
      this.fields = data;
    });
  }
}
