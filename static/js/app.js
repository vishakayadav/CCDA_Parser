var app = angular.module("myApp", ["ngRoute"]);

app.config(function($routeProvider) {
    $routeProvider
    .when("/", {
        templateUrl : "static/ccd.html"
    })
});

app.controller('customersCtrl', function($scope, $http) {
    $scope.ccd = {};

    $scope.init = function () {
      var getFileNames = {
        method:'GET',
        url:'http://localhost:5000/ccd',
        headers: {
          'Content-Type': 'application/json'
        }
      };

      $http(getFileNames).success(function (response, status, headers, config) { 
        console.log(headers());
        $scope.ccd.fileNames = response.filename;
      });
    }

    $scope.display = function(k){
      var req = {
        method:'GET',
        url:'http://localhost:5000/ccd/'+k,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      $http(req).success(function (response) { 
        $scope.ccd.allergies = response.allergies;
        $scope.ccd.encounters = response.encounters;
        $scope.ccd.demographics = response.demographics;
        $scope.ccd.medications = response.medications;
        $scope.ccd.problems = response.problems;
        $scope.ccd.procedures = response.procedures;
        $scope.ccd.providers = response.providers;
        $scope.ccd.results = response.results;
        $scope.ccd.vitals = response.vitals;
      });

    } 
    
    $scope.uploadFile = function(k){
      $scope.ccd.fileUploadData = null;
      var f = document.querySelector('#uploadFile').files[0];
      var r = new FileReader();
      r.onloadend = function(e){
        $scope.ccd.fileUploadData = e.target.result;
        $scope.uploadMyFile($scope.ccd.fileUploadData, f.name);
      }
      r.readAsText(f);
    }; 

    $scope.uploadMyFile = function  (fileData, filename) {
      var fileUpload ={
        method:'POST',
        url:'http://localhost:5000/ccd/upload',
        headers : {
          'Content-Type': 'application/json'
        },
        data : { 
          data : fileData,
          filename : filename
        }
        
      };
      $http(fileUpload).success(function (response) {
        console.log(response);
        $scope.init();
      });
    }

    $scope.exportTheFile = function (k){
      var req = {
        method:'GET',
        url:'http://localhost:5000/ccd/getCSV/'+ $scope.ccd.demographics[1].patient_id + '/' + k,
        headers: {
          'Content-Type': 'application/json'
        }
      }; 
      $http(req).success(function (response) {
        var blob = new Blob([response], { type: 'text/csv;charset=utf-8;' });
        var button = document.querySelector('#exportCsv');
        var url = URL.createObjectURL(blob);
        button.setAttribute("href", url);
        button.click();
        console.log(response);
      });
    }

});