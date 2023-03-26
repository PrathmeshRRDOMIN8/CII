import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:webview_flutter/webview_flutter.dart';

class CameraPage extends StatefulWidget {
  const CameraPage({Key? key}) : super(key: key);

  @override
  _CameraPageState createState() => _CameraPageState();
}

class _CameraPageState extends State<CameraPage> {
  File? image;

  _asyncFileUpload(File file) async{
    // var pic = await http.M.fromPath("file_field", file.path);
    var request = http.post(Uri.parse("http://127.0.0.1:8000"),body: file.path);
    print(request);
  }

  Future pickImage() async {
    try {
      final pImage = await ImagePicker().pickImage(
          source: ImageSource.gallery);
      if (pImage == null)
        return;
      final imageTemp = File(pImage.path);
      // final imageTemp= saveImagePermanently(image!.path);
      setState(() {
        image = imageTemp;
        _asyncFileUpload(image!);
      });
    } on PlatformException catch (e) {
      print('Failed to pick image : $e');
    }
  }

  Future captureImage() async {
    try {
      final cImage = await ImagePicker().pickImage(
          source: ImageSource.camera);
      if (cImage == null)
        return;
      final imageTemp = File(cImage.path);
      // final imagePermanent = saveImagePermanently(image!.path);
      setState(() {
        image = imageTemp;
        _asyncFileUpload(image!);
      });
    } on PlatformException catch (e) {
      print('Failed to pick image : $e');
    }
  }

  Future saveImagePermanently (String Ipath) async {
    final directory = await getApplicationDocumentsDirectory();
    final name = basename(Ipath);
    final image = File('${directory.path}/$name');
    return File(Ipath).copy(image.path);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      body: SafeArea(
        child: WebView(
          initialUrl: 'http://127.0.0.1:8000/docs',
          javascriptMode: JavascriptMode.unrestricted,
          navigationDelegate: (NavigationRequest request) {
            return NavigationDecision.navigate;
          },
        ),
      ),
    );
    // return Container();
  }
}
